"""Client file to request files from the server."""

import cv2
import pickle
import socket
import struct
import sys
import time

sys.path.insert(0, '../include')
import helper

args = helper.parser.parse_args()
frame_count = 0
socket_ops = 0
retrieved_payloads = 0

def cleanup(sock):
    """Closes the connection and performs cleanup."""
    print 'Closing the socket'
    # sock.close()
    cv2.destroyAllWindows()
    clientStatistics()

def clientStatistics():
    """Logs data for tracking client performance."""
    print '\nClient statistics' \
        + '\n-----------------'
    print 'Payloads retrieved:', retrieved_payloads
    print 'Frames displayed:', frame_count
    print 'Socket operations:', socket_ops
    print ''

# Create a UDP socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('localhost', args.client_port))
print 'Connecting to server from address %s:%s' % ('localhost', args.client_port)

# Connect the socket to the server on its listening port.
server_address = ('localhost', args.server_port)
print 'Connecting to %s:%s' % server_address

payload = struct.pack('i', args.client_port) + pickle.dumps('mytoken')
tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tmp_sock.sendto(payload, server_address)

# Restrict the media-player window size to fit the screen.
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

try:
    payload_size = struct.calcsize('l')
    data = ""
    socket_ops = 0

    while True:
        while len(data) < payload_size:
            payload, _ = sock.recvfrom(helper.chunk_size)
            if not payload:
                sys.exit("Server closed the connection")
            data += payload
            socket_ops += 1

        # Retrieve the payload size by unpacking the
        # first 'paylaod_size' bytes.
        packed_chunk_size = data[:payload_size]
        chunk_size = struct.unpack('l', packed_chunk_size)[0]
        retrieved_payloads += 1

        data = data[payload_size:]

        # Retrieve pending payload (if any).
        while len(data) < chunk_size:
            data += sock.recvfrom(helper.chunk_size)[0]
            socket_ops += 1

        serialized_frame = data[:chunk_size]

        # It might be possible that the next payload was
        # retrieved in the above (second) transfer.
        # Update 'data' to contain only the next payload.
        data = data[chunk_size:]

        # Deserialize frames retreived from the payload.
        frame = pickle.loads(serialized_frame)
        cv2.imshow('frame', frame)
        frame_count += 1
        time.sleep(helper.player_sleep_time)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    sys.exit("KeyboardInterrupt encountered")

finally:
    cleanup(sock)
