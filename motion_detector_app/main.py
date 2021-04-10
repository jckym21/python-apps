from motion import Motion_Detection
import os
from plot_motion import plot_motion

def main():
    """
    This app detections motions from a video and plots a motion graph over time.
    Video can be either (1) a save video in the folder venv/example_motion_detection
    or (2) from a webcam on the computer. Motions detected in the video are
    highlight with green boxes in the video.
    """
    folder_path = os.path.dirname(__file__)
    folder_path = os.path.join(folder_path, 'example\\')
    panda_folder_path = (r'example/')
    videos = ['vid.mp4', 'vid2.mov', 'vid3.mp4']
    motion = 'motion_times.csv'

    path = folder_path + videos[2]   # Video path.
    #path = None                       # Webcam

    Motion_Detection(path, folder_path + motion)
    plot_motion(panda_folder_path, motion)

if __name__ == '__main__':
    main()


