"""Client file to request files from the server."""

import cv2
import numpy as np
import pickle
import socket
import struct
import sys

sys.path.insert(0, '..')
import helper

# NOTE: The idea of 'video stream' which is supposed to
# be retrieved is kind of sloppy at the moment. It simply
# represents the video file which is to be retrieved.
args = helper.parser.parse_args()

def cleanup(sock):
    """Closes the connection and performs cleanup."""
    print >> sys.stderr, '~~~~Closing the socket~~~~'
    sock.close()

# Create a TCP/IP socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Connect the socket to the server on its listening port.
server_address = ('localhost', args.port)
print >> sys.stderr, '~~~~Connecting to %s:%s~~~~' % server_address
sock.connect(server_address)

try:
    payload_size = struct.calcsize('Q')
    data = ""

    while True:
        while len(data) < payload_size:
            data += sock.recv(helper.chunk_size)

        # Retrieve the payload size by unpacking the
        # first 'paylaod_size' bytes
        packed_chunk_size = data[:payload_size]
        chunk_size = struct.unpack('Q', packed_chunk_size)[0]

        data = data[payload_size:]

        # Retrieve pending payload (if any)
        while len(data) < chunk_size:
            data += sock.recv(helper.chunk_size)

        frame_data = data[:chunk_size]

        # It might be possible that the next payload was
        # retrieved in the above (second) transfer.
        # Update 'data' to contain only the next payload.
        data = data[chunk_size:]

        # Deserialize frames retreived from the payload.
        frame = pickle.loads(frame_data)
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cleanup(sock)

except KeyboardInterrupt:
    cleanup(sock)
    sys.exit("KeyboardInterrupt encountered")
