# Concurrent feedback-driven video broadcast protocol

## Dependencies
* OpenCV

## Instructions
The current setup performs the transfer locally at localhost.

* Start the server -
  ```
  python server.py <port>
  ```
  This will spawn two processes -
    - The first process starts listening for clients at `localhost:port`.
    - The second process starts capturing frames from the webcam and writes them to a file (currently hardcoded to `serve/output.avi`).

* Start the client -
  ```
  python client.py <port> output.avi
  ```
  This will spawn two processes -
    - The first process will connect to the server and start retrieving video frames, simultaneously saving them to `output.avi` on the client-side.
    - The second process starts a video player which plays the captured stream.
