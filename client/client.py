"""Client file to request and render the live stream from the server."""

import cv2
import numpy as np
import socket
import struct
import sys
import time

sys.path.insert(0, '../include')
import helper

args = helper.parser.parse_args()


def cleanup(sock, frame_count, socket_ops):
    """Closes the connection and performs cleanup."""
    print("Closing the socket")
    sock.close()
    cv2.destroyAllWindows()
    clientStatistics(frame_count, socket_ops)


def clientStatistics(frame_count, socket_ops):
    """Logs data for tracking client performance."""
    print '\nClient statistics' \
            + '\n-----------------'
    print 'Frames displayed:', frame_count
    print 'Socket operations:', socket_ops
    print ''


def main():
    frame_count = 0  # number of frames retrieved
    socket_ops = 0  # number of socket operations (recv) peformed

    # Create a TCP/IP socket.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Connect the socket to the server on its listening port.
    server_address = (args.server_ip, args.port)
    print("Connecting to %s:%s" % server_address)
    sock.connect(server_address)

    # Restrict the media-player window size to fit the screen.
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

    try:
        payload_size = struct.calcsize('Q')
        data = ""

        while True:
            while len(data) < payload_size:
                payload = sock.recv(helper.chunk_size)
                if not payload:
                    sys.exit("Server closed the connection.")
                data += payload
                socket_ops += 1

            # Retrieve the payload size by unpacking the first 'payload_size' bytes.
            packed_frame_dim = data[:payload_size]
            hashed_frame_dim = struct.unpack('Q', packed_frame_dim)[0]

            frame_dims, chunk_size = [], 1
            while hashed_frame_dim:
                dim = hashed_frame_dim & 0xFFFF
                frame_dims += [dim]
                hashed_frame_dim >>= 16
                chunk_size *= dim

            frame_dims.reverse()
            data = data[payload_size:]

            # Retrieve pending payload (if any).
            while len(data) < chunk_size:
                payload = sock.recv(helper.chunk_size)
                if not payload:
                    sys.exit("Server closed the connection.")
                data += payload
                socket_ops += 1

            serialized_frame = data[:chunk_size]

            # It might be possible that the next payload was retrieved in the above
            # (second) transfer. Update 'data' to contain only the next payload.
            data = data[chunk_size:]

            # Deserialize frames retreived from the payload.
            frame = np.fromstring(
                    serialized_frame, dtype='uint8').reshape(frame_dims)
            cv2.imshow('frame', frame)
            frame_count += 1
            time.sleep(helper.player_sleep_time)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        sys.exit("Exiting.")

    finally:
        cleanup(sock, frame_count, socket_ops)


if __name__ == "__main__":
    main()
