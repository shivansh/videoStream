import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server on its listening port
server_address = ('localhost', 8855)
print >> sys.stderr, '~~~~Connecting to %s port %s~~~~' % server_address
sock.connect(server_address)

try:
    # Send data
    message = 'This is a test message.'
    print >> sys.stderr, 'Sending %s bytes' % len(message)
    sock.sendall(message)

    # Wait for a response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        # Receive data in chunks of 32 bytes
        data = sock.recv(32)
        amount_received += len(data)
        print >> sys.stderr, 'Response: %s' % data

    # Check if all data was transmitted back
    assert amount_received == len(data)

finally:
    # Clean up the connection
    print >> sys.stderr, '~~~~Closing the socket~~~~'
    sock.close()
