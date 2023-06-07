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
from configparser import ConfigParser

nSamples = 0
tAverage = 0.0
tMax = 0.0

def config(filename='camera.ini', section='cam_addr'):
    '''
        This routine gets reads the config/init file using the
        library ConfigParser

        Args:
            filename (str): from where retrieve the parameters
            section (str): to retrieve parameters from the filename

        Returns:
            A set with the key:values read for the given section in
            the file.

        Raises:
            Exception: Section not found in the file
            Exception: Error in reading file
    '''

    # Create a parser for reading init file
    # and get the section parameters.
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

if __name__ == "__main__":
    # Collecting data from the Logging File
    try:
        log = config(filename='camera.ini', section='logging')
    except Exception as e:
        print(f"Error reading the logfile: {str(e)}")
        exit(0)
    logfile=log["detector_logfile"]

    # Preparing the logging
    logging.basicConfig(filename=logfile, format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
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
            logging.error("EXCEPTION: " + str(e))
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
