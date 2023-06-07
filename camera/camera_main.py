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
import time
import signal
import shmcam
import timeMetrics
from configparser import ConfigParser

nSamples = 0
tAverage = 0.0
tMax = 0.0
shm = None

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

def handler_SIGINT(signum, frame):
    """
    This routine is the handler for the ^C Interruption from the console.

    Args:
        signum (int): signal number
        frame: stack frame from where the main program was interrupted.

    Returns:
        None

    Raises:
        None
    """
    logging.info("\n\nExiting system. Requesting all modules to finish . . . ")
    shm.setExitFlag(True)
    time.sleep(3)
    try:
        shm.close()
        shm.unlink()
    except Exception as e:
        logging.error(f"EXCEPTION AT EXITING: {str(e)}")
    exit(0)

if __name__ == "__main__":
    
    # Collecting data from the config file
    try:
        db = config(filename='camera.ini', section='logging')
    except Exception as e:
        print(f"Error reading the source: {str(e)}")
        exit(0)
    logfile = db["main_logfile"]
    print(f"Logfile set to {logfile}")
    
    # Preparing the logging and metrics
    logging.basicConfig(format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("Program started")
    metrics = timeMetrics.timeMetrics()

    # Create area of shared memory
    shm = shmcam.SHMCAM(create=True, name="CAMERA_SHMEM",maxImageWidth=1280, maxImageHeight=720)

    # Wait for others to join if needed
    # then initiate the running
    time.sleep(1)
    # Set the flag to capture video
    shm.setCaptureFlag(True)
    logging.info(f"Capture Flag: {shm.getCaptureFlag()}")
    # Set the flag to allow view of the video in a screen
    shm.setViewFlag(True)
    logging.info(f"View Flag: {shm.getViewFlag()}")
    # Set the flag to allow object detection
    shm.setYoloFlag(True)
    logging.info(f"Yolo Flag: {shm.getYoloFlag()}")
    # Set the flag to allow object detection
    shm.setRecordFlag(True)
    logging.info(f"Record Flag: {shm.getRecordFlag()}")
    # Set the marker of objects on the image
    shm.setMarkFlag(True)
    logging.info(f"Mark Flag: {shm.getMarkFlag()}")
    # Set the flag running
    shm.setRunFlag(True)
    logging.info(f"Run Flag: {shm.getRunFlag()}")
    # Set the flag exit
    shm.setExitFlag(False)
    logging.info(f"Exit Flag: {shm.getExitFlag()}")
    # Set the pipe flag
    shm.setPipeFlag(False)
    logging.info(f"Pipe Flag: {shm.getPipeFlag()}")

    # Callback signal for SIGINT
    signal.signal(signal.SIGINT, handler_SIGINT)

    while True:
        try:
            metrics.newCycle()

            # Do some staff for the main program
            # . . .

            # Calculate metrics
            print(f"\r{metrics.endCycle().toString()}", end="", flush=True)

        except Exception as e:
            logging.error(str(e))
            pass
