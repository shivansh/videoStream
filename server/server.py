"""Server file to serve files requested by the connecting clients."""

import cv2
import pickle
import socket
import struct
import sys
import time
from threading import Thread
from Queue import Queue

sys.path.insert(0, '../include')
import helper

args = helper.parser.parse_args()

# TODO (shivansh) Replace queue with say, a list ; the
# current implementation is buggy as it will work only
# if there is a single consumer as the payload is always
# dequeued and sent over the socket. An ideal implementation
# will maintain a list of payloads to be served, and each
# consumer should keep track of the last payload which it
# served and look out for next payload (if ready) in the list.
q = Queue()

# Start stream and adjust screen resolution.
cap = cv2.VideoCapture(0)
frame_width = 160
frame_height = 120
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

def webcamFeed():
    """Collects frames from the webcam."""
    data = ""
    global q

    while True:
        ret, frame = cap.read()
        # Serialize the frames
        data += pickle.dumps(frame)

        # Each data chunk comprises of the following:
        #       +--------------+--------------+
        #       | Payload size |   Payload    |
        #       |   (Packed)   | (Serialized) |
        #       +--------------+--------------+
        #
        # Collect 'helper.chunk_size' worth of
        # payload before starting the transfer.
        if len(data) >= helper.chunk_size:
            q.put(struct.pack('l', len(data)) + data)
            data = ""
            # Yield CPU so that the thread corresponding
            # to 'handleConnection' is scheduled.
            time.sleep(0)

def handleConnection(connection, client_address):
    """Handles an individual client connection."""
    print 'handle'
    global q

    print >> sys.stderr, 'Connection from', client_address
    print >> sys.stderr, 'Starting broadcast'

    while True:
        if not q.empty():
            connection.sendall(q.get())
        else:
            # Yield CPU so that the thread corresponding
            # to 'webcamFeed' is scheduled.
            time.sleep(0)

def cleanup(connection):
    """Closes the connection and performs cleanup."""
    cv2.destroyAllWindows()
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
    # Start a thread to collect frames and generate
    # payload to be served to the clients.
    payload_thread = Thread(target = webcamFeed)
    payload_thread.setDaemon(True)
    payload_thread.start()

    while True:
        # Wait for a connection.
        print >> sys.stderr, '~~~~Waiting for a connection~~~~'
        connection, client_address = sock.accept()

        # Start a consumer thread corresponding to
        # each connected client.
        consumer_thread = Thread(target = handleConnection,
                                 args = (connection, client_address))
        consumer_thread.setDaemon(True)
        consumer_thread.start()

except KeyboardInterrupt:
    cleanup(connection)
    sys.exit("KeyboardInterrupt encountered")

finally:
    cleanup(connection)
