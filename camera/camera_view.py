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
import timeMetrics

nSamples = 0
tAverage = 0.0
tMax = 0.0
frame = None
boxes = []

def config(filename='camera.ini', section='logging'):
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
        # Collecting data from the config file
    try:
        db = config(filename='camera.ini', section='logging')
    except Exception as e:
        print(f"Error reading the source: {str(e)}")
        exit(0)
    logfile = db["view_logfile"]

    # Preparing the logging and metrics
    logging.basicConfig(filename=logfile, format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("Program started")
    metrics = timeMetrics.timeMetrics()

    # Create area of shared memory
    shm = shmcam.SHMCAM(create=False, name="CAMERA_SHMEM")

    # Wait until run flag is activated
    while not shm.getRunFlag():
        logging.info("Waiting ......")
        pass

    while True:

        metrics.newCycle()

        if shm.getRunFlag() and shm.getViewFlag():
            try:
                # Display the video
                frame = shm.getImage()

                # if detector is activated, modify image with detections
                if shm.getYoloFlag():

                    boxes = shm.getBoxes()

                    for box in boxes:
                        #font = cv2.FONT_HERSHEY_PLAIN
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        x, y, w, h = box[0]
                        label = box[1]
                        confidence = box[2]
                        color = box[3]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, label + ' ' + str(round(confidence*100)) + '%', (x-10, y-10), font, 1 / 2, color, 2)


                cv2.imshow("Video", frame)

            except Exception as e:
                logging.error("Error Getting Image, Boxes or printing boxes: " + str(e))
                pass

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if shm.getExitFlag():
            break

        # Calculate metrics
        print(f"\r{metrics.endCycle().toString()}", end="", flush=True)

    logging.info("Exiting view program")
    shm.close()
