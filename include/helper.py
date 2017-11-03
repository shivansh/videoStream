"""Helper functions and declarations common to server and client."""

import argparse

# To reduce the number of thread switches between
# the the 'webcamFeed' and 'handleConnection' threads,
# the individual payload size is kept large (1 MB).
chunk_size = 2097152

parser = argparse.ArgumentParser(description='',
                                 add_help = False)
parser.add_argument('-h', '--help',
                    action='help',
                    default=argparse.SUPPRESS)
parser.add_argument('port',
                    type = int,
                    help = 'Server port number')

def readFileInChunks(file_object, chunk_size):
    """Lazy function to read file in 'chunk_size' byte chunks.
    Returns a generator.
    """
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
