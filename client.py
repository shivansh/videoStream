"""Client file to request files from the server."""
import filecmp
import os
import socket
import sys

import helper

received_file_name = 'received_file'

def cleanup(sock):
    """Closes the connection and performs cleanup."""
    print >> sys.stderr, '~~~~Closing the socket~~~~'
    sock.close()

"""Create a TCP/IP socket."""
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

"""Connect the socket to the server on its listening port."""
server_address = ('localhost', helper.socket)
print >> sys.stderr, '~~~~Connecting to %s port %s~~~~' % server_address
sock.connect(server_address)

try:
    if os.path.isfile(received_file_name):
        os.remove(received_file_name)

    f = open(received_file_name, 'a')

    while True:
        chunk = sock.recv(helper.chunk_size)
        if not chunk:
            break
        f.write(chunk)

    f.close()

except KeyboardInterrupt:
    cleanup(connection)

finally:
    """Check if files match."""
    if filecmp.cmp('serve/test_file', 'received_file'):
        print >> sys.stderr, 'File transfer successful, files match!'
    else:
        print >> sys.stderr, 'Invalid file transfer'

    cleanup(sock)
