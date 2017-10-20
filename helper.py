"""Helper functions and declarations common to server and client."""

import argparse

"""The chunk size is currently set to a non-realistic value of
32 bytes to demonstrate file transfers when chunk sizes are
smaller than the file size.
"""
chunk_size = 32
serve_dir = 'serve/'  # Directory from where the server serves.

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
