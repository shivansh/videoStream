"""Server file to serve files requested by the connecting clients."""

import cv2
import datetime
import errno
import pickle
import socket
import struct
import sys
import time
from threading import Thread
from Queue import Queue

sys.path.insert(0, '../include')
import helper

# Define the globals
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

consumer_thread_yields = 0  # Total CPU yields for 'handleConnection'
webcam_thread_yields = 0    # Total CPU yields for 'webcamFeed'
consumer_thread_count = 0
connection = None
frames_per_payload = 0
payload_count = 0

def webcamFeed():
    """Constructs a payload from the frames collected from
    the webcam and inserts them into a global queue.
    """
    data = ""
    count_frames = 0
    generated_payloads = 0
    global q, webcam_thread_yields, frames_per_payload, avg_payload_gen_time

    while True:
        ret, frame = cap.read()
        # Serialize the frames
        data += pickle.dumps(frame)
        count_frames += 1

        # Each data chunk comprises of the following:
        #       +--------------+--------------+
        #       | Payload size |   Payload    |
        #       |   (Packed)   | (Serialized) |
        #       +--------------+--------------+
        #
        # Collect 'helper.chunk_size' worth of
        # payload before starting the transfer.
        if len(data) >= helper.chunk_size:
            generated_payloads += 1
            q.put(struct.pack('l', len(data)) + data)
            data = ""

            if frames_per_payload == 0:
                frames_per_payload = count_frames

            # Yield CPU after generating 3 payloads.
            # The average payload generation time (on my machine)
            # is 0.03 seconds. Thus, generating 10 payloads will
            # take approximately 0.3 seconds, which is the duration
            # for which consumer thread sleeps.
            if generated_payloads == 10:
                generated_payloads = 0
                webcam_thread_yields += 1
                time.sleep(0.2)

def handleConnection(connection, client_address, thread_id):
    """Handles an individual client connection."""
    global q, consumer_thread_yields, payload_count

    print 'Thread %d: Connection from %s' % (thread_id, client_address)
    print 'Thread %d: Starting broadcast' % thread_id

    try:
        while True:
            # The time take to serve 10 payloads is -
            # (3 * 10^(-5)) + (10*0.02) = 0.2 (approx.)
            if not q.empty():
                payload_count += 1
                connection.sendall(q.get())
                time.sleep(0.02)
            else:
                # Yield CPU so that the thread corresponding
                # to 'webcamFeed' is scheduled.
                consumer_thread_yields += 1
                time.sleep(0.3)

    except socket.error, e:
        if isinstance(e.args, tuple):
            if e[0] == errno.EPIPE:
                print >> sys.stderr, 'Client disconnected'
            else:
                # TODO Handle other socket errors.
                pass
        else:
            print >> sys.stderr, 'Socket error', e

    except IOError, e:
        print >> sys.stderr, 'IOError:', e

def cleanup(connection):
    if connection:
        """Closes the connection and performs cleanup."""
        cv2.destroyAllWindows()
        print 'Closing the socket'
        connection.close()

def serverStatistics():
    """Logs data for tracking server performance."""
    print '\nServer statistics' \
        + '\n-----------------' \
        + '\nNo. of CPU yields -'
    print '  * handleConnection:', consumer_thread_yields
    print '  * webcamFeed:', webcam_thread_yields
    print 'Frames per payload:', frames_per_payload
    print 'Payloads delivered:', payload_count
    print ''

# Create a TCP/IP socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to a port.
server_address = ('localhost', args.port)
print 'Starting up on %s:%s' % server_address
sock.bind(server_address)

# Listen for incoming connections.
sock.listen(5)

# Start a thread to collect frames and generate
# payload to be served to the clients.
webcam_thread = Thread(target = webcamFeed)
webcam_thread.setDaemon(True)
webcam_thread.start()

try:
    while True:
        print 'Thread %d: Waiting for a connection' % consumer_thread_count
        connection, client_address = sock.accept()

        # Start a consumer thread corresponding to
        # each connected client.
        consumer_thread = Thread(target = handleConnection,
                                 args = (connection,
                                         client_address,
                                         consumer_thread_count))
        consumer_thread_count += 1
        consumer_thread.setDaemon(True)
        consumer_thread.start()

except KeyboardInterrupt:
    cleanup(connection)
    serverStatistics()
    sys.exit("KeyboardInterrupt encountered")

finally:
    cleanup(connection)
