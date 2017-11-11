# Concurrent feedback-driven video broadcast protocol

## Dependencies
* OpenCV (3.2.0)
* numpy

## Instructions
The current setup performs the transfer locally at localhost.

* Start the server -
  ```
  python server.py <port>
  ```
  Retrieve a collection of frames (currently 4096 bytes) from the webcam and construct the following chunk to be transferred -
  ```
        +------------------+---------------+
        | Frame dimensions |     Frame     |
        |     (Hashed)     | (byte string) |
        +------------------+---------------+
  ```

* Start the client -
  ```
  python client.py <port>
  ```
  This will retrieve the payload from server, unpack and convert to numpy array appropriately and render the frames on the fly.
