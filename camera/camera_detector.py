# TheBlackmad
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import cv2
import time
import shmcam
import numpy as np
import YOLO_Detector as yolo
import timeMetrics

nSamples = 0
tAverage = 0.0
tMax = 0.0

if __name__ == "__main__":
    # Preparing the logging
    logging.basicConfig(format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("Program started")
    metrics = timeMetrics.timeMetrics()

    # Create area of shared memory
    shm = shmcam.SHMCAM(create=False, name="CAMERA_SHMEM")

    # Initialize the Yolo detector
    if shm.getYoloFlag():
        logging.info("Initializing the YOLO Detector . . .")
        try:
            # Initialize the Yolo detector
            detector = yolo.YOLO_Detector()
        except Exception as e:
            logging.error("PUTA EXCEPTION: " + str(e))
            exit(-1)

    # Wait until run flag is activated
    while not shm.getRunFlag():
        logging.info("Waiting ......")
        pass

    frame = None
    while True:

        metrics.newCycle()

        if shm.getYoloFlag() and shm.getRunFlag():
            try:
                # Find the objects
                frame = shm.getImage()

                #boxes = detector.detectObjects(frame)
                boxes = detector.detect(frame)

                shm.setBoxes(boxes)

            except Exception as e:
                logging.error(str(e))

        if shm.getExitFlag():
            break

        # Calculate metrics
        print(f"\r{metrics.endCycle().toString()}", end="", flush=True)

    logging.info("Exiting view program")
    shm.close()
