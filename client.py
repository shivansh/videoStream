"""Client file to request files from the server."""

from multiprocessing import Process
import os
import socket
import sys

import helper
import video_player

# NOTE: The idea of 'video stream' which is supposed to
# be retrieved is kind of sloppy at the moment. It simply
# represents the video file which is to be retrieved.
helper.parser.add_argument('file',
                           type = str,
                           help = 'Video stream which will be requested from server. This is currently hardcoded to \'output.avi\'')
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
    if os.path.isfile(args.file):
        os.remove(args.file)

    # Send the stream name to server.
    sock.sendall(args.file)

    f = open(args.file, 'a')

    # Spawn a process to play the retrieved video stream.
    video_player_process = Process(target = video_player.playVideo(helper.serve_dir + args.file))
    video_player_process.daemon = True
    video_player_process.start()

    while True:
        chunk = sock.recv(helper.chunk_size)
        if not chunk:
            break
        f.write(chunk)

    f.close()

except KeyboardInterrupt:
    sys.exit("KeyboardInterrupt encountered")

finally:
    cleanup(sock)
