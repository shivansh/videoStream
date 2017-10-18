import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a port
server_address = ('localhost', 8855)
print >> sys.stderr, '~~~~Starting up on %s port %s~~~~' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >> sys.stderr, '~~~~Waiting for a connection~~~~'
    connection, client_address = sock.accept()

    try:
        print >> sys.stderr, 'Connection from', client_address

        # Receive data in chunks of 32 bytes
        while True:
            data = connection.recv(32)
            print >> sys.stderr, 'Received: %s' % data
            if data:
                # Retransmit received data
                print >> sys.stderr, 'Acknowledging with %s bytes' % len(data)
                connection.sendall(data)
            else:
                print >> sys.stderr, 'No more data from', client_address
                break

    finally:
        # Clean up the connection
        print >> sys.stderr, '~~~~Closing the socket~~~~'
        connection.close()
