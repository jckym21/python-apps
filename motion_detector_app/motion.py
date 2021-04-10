import cv2
import time
import numpy as np
from imutils.video import VideoStream
import imutils
from datetime import datetime
import matplotlib.pyplot as plt
from imutils.object_detection import non_max_suppression
import os

class Motion_Detection():
    """
    This class takes a video and detects area of motions in the video. Area of motion
    is highlighted with green rectangles and displayed along with a video showing delta
    of the current frame with an averaged background and a video showing threshold
    area of motion. Video source can either be from either (1) a saved file in which the
    file path is provided as an argument or (2) the webcam in which the file path is
    empty.
    """
    def __init__(self, path, log):
        self.path = path                     # Video file path
        self.motion_log = log                # Motion log file path
        self.avg_frame = None                # Initialize average frame variable
        self.last_frame_motion = False       # Flag for motion in the last frame
        self.current_frame_motion = False    # Flag for motion in the current frame
        self.frameDelta = None               # Initialize frame delta frame variable
        self.threshold = None                # Initialize/rest frame threshold frame variable

        self.MIN_DETECTION_AREA = 200        # 50 for videos
        self.FRAME_WEIGHT = 0.05             # 0.05 works well for [1] and [0]

        with open(self.motion_log, 'w') as f:
            f.write('start,end')

        if self.path is None:
            self.vs = VideoStream(src=0).start()  # Obtain video from webcam
            time.sleep(2.0)                       # Give 2 seconds for camera to warm up
        else:
            self.vs = cv2.VideoCapture(path)      # Obtain video from file

        while True:
            # Obtain and process one frame at a time
            self.frame = self.vs.read()

            if self.path is not None:
                self.frame = self.frame[1]        # For video, grab the frame read
            if self.frame is None:                # Capture end of video time in case of motion detected in last frame
                self.current_frame_motion = False
                self.write_motion_time()
                break
            self.text = "Unoccupied"
            self.current_frame_motion = False

            # Resize and perform gaussian blur
            self.resize_and_blur()

            # Update background average frame
            self.update_bg()

            # Remove frame from background
            self.remove_bg()

            # Find motion contours and draw rectangle around motion
            self.rect = []  # Initialize/reset motion rectangle boxs variable
            self.find_contour()
            self.draw_motion()
            self.last_frame_motion = self.current_frame_motion

            # Draw text and timestamp on frame
            self.add_status_timestamps()

            # Display videos
            cv2.imshow("Security Feed", self.frame)
            cv2.imshow("Frame Delta", self.frameDelta)
            cv2.imshow("Mask", self.threshold)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.current_frame_motion = False
                self.write_motion_time()
                break
        if self.path is None:
            self.vs.stop()
        else:
            self.vs.release()
        cv2.destroyAllWindows()

    # Draws rectangles in an image with non-max-suppression to group boxes lumped together
    def draw_detections(self, thickness=1):
        self.rect = np.array([[x, y, x + w, y + h] for (x, y, w, h) in self.rect])
        pick = non_max_suppression(self.rect, probs=None, overlapThresh=100)  # Default threshold 0.65
        for (xA, yA, xB, yB) in pick:
            cv2.rectangle(self.frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

    # Writes starts and end time of detected motion
    def write_motion_time(self):
        with open(self.motion_log, 'a') as f:
            if self.last_frame_motion == False and self.current_frame_motion == True:
                # This is motion start up time
                f.write('\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ',')
            elif self.last_frame_motion == True and self.current_frame_motion == False:
                # This is motion end time
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Calculate delta from weight background
    def remove_bg(self):
        self.frameDelta = cv2.absdiff(self.gray, cv2.convertScaleAbs(self.avg_frame))

    # Update weighted background
    def update_bg(self):
        if self.avg_frame is None:
            # Add in the first frame for averaging
            self.avg_frame = self.gray.copy().astype("float")
        else:
            # Calculates a running average
            cv2.accumulateWeighted(self.gray, self.avg_frame, self.FRAME_WEIGHT)

    # Resize and perform gaussian blur on frame
    def resize_and_blur(self):
        # Resize and perform gaussian blur
        self.frame = imutils.resize(self.frame, width=500)
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.gray = cv2.GaussianBlur(self.gray, (21, 21), 0)

    # Find contours and append bounding rectangle to list
    def find_contour(self):
        # Create clean mask using threshold, hole filling and finding contour
        self.threshold = cv2.threshold(self.frameDelta, 10, 255, cv2.THRESH_BINARY)[1]
        self.threshold = cv2.dilate(self.threshold, None, iterations=8)
        contour = cv2.findContours(self.threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour = imutils.grab_contours(contour)

        # Append motion box
        for c in contour:
            if cv2.contourArea(c) >= self.MIN_DETECTION_AREA:
                self.rect.append(cv2.boundingRect(c))

    # Add bounding rectangles to frame and set motion flag
    def draw_motion(self):
        self.draw_detections(self.frame)
        if len(self.rect) != 0:
            self.text = "Motion Detected"
            self.current_frame_motion = True
        else:
            self.current_frame_motion = False
        self.write_motion_time()

    # Add motion status and timestamp onto frame
    def add_status_timestamps(self):
        # Draw text and timestamp on frame
        cv2.putText(self.frame, "Status: {}".format(self.text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        t = datetime.now().strftime("%A %B %d %Y %I:%M:%S%p")
        cv2.putText(self.frame, t, (10, self.frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # Rescale frame
    def rescale_frame(self, percent=75):
        width = int(self.frame.shape[1] * percent/ 100)
        height = int(self.frame.shape[0] * percent/ 100)
        dim = (width, height)
        return cv2.resize(self.frame, dim, interpolation =cv2.INTER_AREA)