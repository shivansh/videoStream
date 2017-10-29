import cv2
import time

def playVideo(video_name):
    """Plays the video frames retrieved from the stream."""
    cap = cv2.VideoCapture(video_name)

    while(cap.isOpened()):
        ret, frame = cap.read()

        # Frame validation will not (possibly) slow
        # things down if performed at the endpoints.
        if ret == True:
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # TODO A better/precise way of rendering at 1x speed
        time.sleep(0.04)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
