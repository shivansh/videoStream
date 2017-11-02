# Concurrent feedback-driven video broadcast protocol

## Dependencies
* OpenCV (3.2.0)

## Instructions
The current setup performs the transfer locally at localhost.

* Start the server -
  ```
  python server.py <port>
  ```
  Retrieve a collection of frames (currently 4096 bytes) from the webcam and construct the following chunk to be transferred -
  ```
      +--------------+--------------+
      | Payload size |   Payload    |
      |   (Packed)   | (Serialized) |
      +--------------+--------------+
  ```

* Start the client -
  ```
  python client.py <port> output.avi
  ```
  This will retrieve the payload from server, unpack and desiarialize appropriately and render the frames on the fly.
