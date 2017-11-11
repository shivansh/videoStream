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
max_concurrent_clients = 5
max_payload_count = 10 * max_concurrent_clients

# Initialize a constant-sized list of payloads.
payload_list = [None] * max_payload_count

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
payload_count = 0
last_written_index = 0

def webcamFeed():
    """Constructs a payload from the frames collected from
    the webcam and inserts them into a global list.
    """
    global webcam_thread_yields, payload_list, last_written_index
    payload = ""
    frame_count = 0
    generated_payloads = 0
    write_index = 0

    while True:
        ret, frame = cap.read()
        # Serialize the frames
        serialized_frame = pickle.dumps(frame)
        payload += struct.pack('l', len(serialized_frame)) + serialized_frame
        frame_count += 1

        # Each payload comprises of 'frames_per_payload'
        # number of the following structures -
        #       +------------+--------------+
        #       | Frame size |    Frame     |
        #       |  (Packed)  | (Serialized) |
        #       +------------+--------------+
        #
        # Collect 'helper.chunk_size' worth of
        # payload before starting the transfer.
        if frame_count == helper.frames_per_payload:
            generated_payloads += 1

            # Update the list of payloads.
            payload_list[write_index] = payload
            if __debug__:
                print 'Populating index', write_index
            last_written_index = write_index
            write_index = (write_index+1) % max_payload_count

            payload = ""
            frame_count = 0

            # Yield CPU after generating 1 payload.
            # The average payload generation time (on my machine)
            # is approximately 0.01 seconds.
            if generated_payloads == 10:
                generated_payloads = 0
                webcam_thread_yields += 1

def handleConnection(connection, client_address, thread_id):
    """Handles an individual client connection."""
    global q, consumer_thread_yields, payload_count

    # Sleep duration between two socket operations.
    wait_after_serve = helper.frames_per_payload * helper.player_sleep_time

    # The instant when the consumer was created, it should start
    # broadcasting frames which were generated closest to that
    # instant. 'last_written_index' is used to keep track of this.
    index = last_written_index

    # Check if the writer has populated the index'th entry of the
    # list. This is only useful for the case if the client was started
    # before the server could entirely populate 'payload_list'.
    if not payload_list[index]:
        index = 0

    # Duration for which consumer waits on the webcam
    # thread to fill up the queue with payloads.
    wait_for_writer = helper.frames_per_payload / 10.0

    print 'Thread %d: Connection from %s' % (thread_id, client_address)
    print 'Thread %d: Starting broadcast' % thread_id

    served_payloads = 0

    try:
        while True:
            # Ensure that reader is always behind the writer.
            if index == last_written_index:
                if __debug__:
                    print 'Covered up, waiting for writer'
                consumer_thread_yields += 1
                time.sleep(wait_for_writer)
            else:
                if __debug__:
                    print 'Sending index', index
                payload_count += 1
                connection.sendall(payload_list[index])
                served_payloads += 1
                index = (index+1) % max_payload_count

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
    """Closes the connection and performs cleanup."""
    if connection:
        cv2.destroyAllWindows()
        print 'Closing the socket'
        connection.close()
        serverStatistics()

def serverStatistics():
    """Logs data for tracking server performance."""
    print '\nServer statistics' \
        + '\n-----------------' \
        + '\nNo. of CPU yields -'
    print '  * handleConnection:', consumer_thread_yields
    print '  * webcamFeed:', webcam_thread_yields
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
sock.listen(max_concurrent_clients)

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
    sys.exit("KeyboardInterrupt encountered")

finally:
    cleanup(connection)
