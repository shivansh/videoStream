import pickle
import socket
import struct
import sys

sys.path.insert(0, '../include')
import helper

local_port = 2051
server_addr = ('localhost', 2048)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('localhost', local_port))

sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

payload = struct.pack('i', local_port) + pickle.dumps('mytoken')

sock2.sendto(payload, server_addr)

print 'Trying to receive data from server on addr: %s:%s' % ('localhost', local_port)
data, _ = sock.recvfrom(helper.chunk_size)

print(data)
