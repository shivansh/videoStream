import cv2
import time

def playVideo(video_name):
    """Plays the video frames retrieved from the stream."""
    # Wait for 1 second after the transfer initiates so that
    # enough frames accumulate before rendering begins.
    time.sleep(1)
    cap = cv2.VideoCapture(video_name)

    while(cap.isOpened()):
        ret, frame = cap.read()

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # TODO A better/precise way of rendering at 1x speed
        time.sleep(0.04)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
