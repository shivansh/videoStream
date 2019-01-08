# Concurrent feedback-driven video broadcast protocol

## Dependencies
* OpenCV (3.2.0)
* numpy

## Implementation overview
An overview of the implemented design -  

![Implementation-Design](report/design.png)

### The reader-writer model
The implemented reader-writer model depicting 3 concurrent readers -  
![Reader-Writer-Model](report/reader_writer.png)

### [Project Report](report/cs425-mini-project.pdf)

## Instructions

For quick testing purposes, run `./run.sh`. This script starts a server and client process.

The current setup performs the transfer locally at localhost.

To run the individual components, follow the instructions below.

* Start the server -
  ```
  python3 -O server.py -p <port>
  ```
  To enable debug mode, remove the `-O` flag.  
  The server retrieves `frames_per_payload` number of frames from the webcam and constructs the following payload which is transferred -    
![Payload-Structure](report/payload_structure.png)

* Start the client -
  ```
  python3 client.py -p <port>
  ```
  This will retrieve the payload from server, unpack and convert to numpy array appropriately, rendering the frames on the fly.
