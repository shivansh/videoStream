import cv2
import os

def captureFrames(output_file):
    """Capture video frames from webcam and writes to disk."""
    if os.path.isfile(output_file):
        os.remove(output_file)

    cap = cv2.VideoCapture(0)

    # Define the codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # Create a VideoWriter object
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    while(cap.isOpened()):
        ret, frame = cap.read()

        # Frame validation will not (possibly) slow
        # things down if performed at the endpoints.
        if ret == True:
            out.write(frame)    # write the frame
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Cleanup
    cap.release()
    out.release()
    cv2.destroyAllWindows()
