"""Helper functions and declarations common to server and client."""

import argparse

# The frame size is evaluated with respect to the current image quality.
# TODO: do this computation during runtime.
frame_size = 1728080
frames_per_payload = 1
chunk_size = frame_size * frames_per_payload

# The duration between rendering two adjacent frames.
player_sleep_time = 0.02

parser = argparse.ArgumentParser(description='', add_help=False)
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS)
parser.add_argument(
    '-s',
    '--server_ip',
    type=str,
    default='localhost',
    help='Server IP address')
parser.add_argument(
    '-p', '--port', type=int, default=8080, help='Server port number')


def readFileInChunks(file_object, chunk_size):
    """Lazy function to read file in 'chunk_size' byte chunks.
    Returns a generator.
    """
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
