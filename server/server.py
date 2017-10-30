"""Server file to serve files requested by the connecting clients."""

import cv2
import numpy as np
import pickle
import socket
import struct
import sys
from multiprocessing import Process

sys.path.insert(0, '..')
import helper

args = helper.parser.parse_args()

def handleConnection(connection, client_address):
    """Handles an individual client connection."""
    print >> sys.stderr, 'Connection from', client_address
    print >> sys.stderr, 'Starting broadcast'

    cap = cv2.VideoCapture(0)

    while True:
        data = ""
        ret, frame = cap.read()
        # Serialize the frames
        data += pickle.dumps(frame)

        # Each data chunk comprises of the following:
        #       +--------------+--------------+
        #       | Payload size |   Payload    |
        #       |   (Packed)   | (Serialized) |
        #       +--------------+--------------+
        if len(data) >= helper.chunk_size:
            # Collect 'helper.chunk_size' worth of
            # payload before starting the transfer.
            connection.sendall(struct.pack('Q', len(data)) + data)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

def cleanup(connection):
    """Closes the connection and performs cleanup."""
    print >> sys.stderr, '~~~~Closing the socket~~~~'
    connection.close()

# Create a TCP/IP socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to a port.
server_address = ('localhost', args.port)
print >> sys.stderr, '~~~~Starting up on %s:%s~~~~' % server_address
sock.bind(server_address)

# Listen for incoming connections.
sock.listen(5)
connection = ""

try:
    while True:
        # Wait for a connection.
        print >> sys.stderr, '~~~~Waiting for a connection~~~~'
        connection, client_address = sock.accept()

        # The connection should be handled by another child 'process'.
        p = Process(target = handleConnection, args = (connection, client_address))
        p.daemon = True
        p.start()

except KeyboardInterrupt:
    cleanup(connection)
    sys.exit("KeyboardInterrupt encountered")

finally:
    cleanup(connection)
