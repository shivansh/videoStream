"""Server file to serve files requested by the connecting clients."""

import socket
import sys

import helper

args = helper.parser.parse_args()

def cleanup(connection):
    """Closes the connection and performs cleanup."""
    print >> sys.stderr, '~~~~Closing the socket~~~~'
    connection.close()

"""Create a TCP/IP socket."""
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

"""Bind the socket to a port."""
server_address = ('localhost', args.port)
print >> sys.stderr, '~~~~Starting up on %s:%s~~~~' % server_address
sock.bind(server_address)

"""Listen for incoming connections."""
sock.listen(1)

try:
    while True:
        """Wait for a connection."""
        print >> sys.stderr, '~~~~Waiting for a connection~~~~'
        connection, client_address = sock.accept()

        try:
            print >> sys.stderr, 'Connection from', client_address
            print >> sys.stderr, 'Starting file transfer'

            """Retrieve the requested filename from client."""
            filename = connection.recv(32)

            if filename:
                f = open(helper.serve_dir + filename)
                for chunk in helper.readFileInChunks(f, helper.chunk_size):
                    connection.sendall(chunk)

            print >> sys.stderr, 'File transfer complete'
            f.close()

        finally:
            cleanup(connection)

except KeyboardInterrupt:
    sys.exit()
