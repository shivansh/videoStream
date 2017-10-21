"""Client file to request files from the server."""

import filecmp
import os
import socket
import sys

import helper

helper.parser.add_argument('file',
                           type = str,
                           help = 'Filename which will be requested from server')
args = helper.parser.parse_args()

def cleanup(sock):
    """Closes the connection and performs cleanup."""
    print >> sys.stderr, '~~~~Closing the socket~~~~'
    sock.close()

"""Create a TCP/IP socket."""
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

"""Connect the socket to the server on its listening port."""
server_address = ('localhost', args.port)
print >> sys.stderr, '~~~~Connecting to %s:%s~~~~' % server_address
sock.connect(server_address)

try:
    if os.path.isfile(args.file):
        os.remove(args.file)

    """Send the filename to server."""
    sock.sendall(args.file)

    f = open(args.file, 'a')

    while True:
        chunk = sock.recv(helper.chunk_size)
        if not chunk:
            break
        f.write(chunk)

    f.close()

except KeyboardInterrupt:
    cleanup(sock)
    sys.exit("KeyboardInterrupt encountered")

finally:
    """FIXME: This segment seems to run even when KeyboardInterrupt
    is encountered.
    """

    """Validate correctness of the file-transfer."""
    if filecmp.cmp(helper.serve_dir + args.file, args.file):
        print >> sys.stderr, 'File transfer successful, files match!'
    else:
        print >> sys.stderr, 'Invalid file transfer'

    cleanup(sock)
