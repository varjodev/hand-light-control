import cv2
import numpy as np
from datetime import datetime
from pprint import pprint
from collections import deque
from scipy import ndimage

import utils
from light import Light
from camera import HTTPCamera
from postprocessor import PostProcessor
from keyhandler import KeyHandler
from detector import FingerCounter

camera_url = "http://192.168.50.14"
cam = HTTPCamera(camera_url=camera_url, config_json="camera_config.json", config_name="myconfig")

postprocess_params = {"postprocess_bool":False,
                      "rotation": 90,
                      "fft": True,
                      "fft_filter": False,
                      "edges": False,
                      "blur": False,
                      "average": False,
                      "threshold": False
                    }

pproc = PostProcessor(postprocess_params)
kh = KeyHandler(cam, pproc)
fc = FingerCounter()
l = Light()

finger_brightness_table = [0,50,100,170,200,255]

dims = None
R = None

complex_frame = None

cap = cv2.VideoCapture(cam.url + ":81/stream")

frame_counter = 0
frame_counter_reset = 10
while True:
    if cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Didn't get frame")
            continue

        if pproc.params["postprocess_bool"]:
            frame = pproc.processing_stack(frame)

        # Hand detection and finger counting
        frame = fc.process(frame)
        num = fc.count()

        if frame_counter == frame_counter_reset:
            # print(f"Detected fingers: {num}")
            # print()
            if num is not None:
                if num == 0:
                    print("Light off")
                    l.off()
                else:
                    l.brightness(finger_brightness_table[num])
            frame_counter = 0

        cv2.imshow("frame", frame)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break

        elif key == ord('s'): # Save a screenshot
            cv2.imwrite(f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", frame)

        elif key == ord('.'):
            cv2.waitKey(0)

        else:
            kh.handle(key)

        frame_counter += 1

        

            

cv2.destroyAllWindows()
cap.release()