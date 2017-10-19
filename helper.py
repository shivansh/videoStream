"""Helper functions and declarations common to server and client."""

"""The chunk size is currently set to 32 bytes to demonstrate
file transfers when chunk sizes are smaller than the file size.
"""
chunk_size = 32
port = 2248

def readFileInChunks(file_object, chunk_size):
    """Lazy function to read file in "chunk_size" byte chunks.
    Returns a generator.
    """
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
