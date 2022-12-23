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

nSamples = 0
tAverage = 0.0
tMax = 0.0
shm = None

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
    # Set the flag to allow view of the video in a screen
    shm.setViewFlag(True)
    # Set the flag to allow object detection
    shm.setYoloFlag(True)
    # Set the flag to allow object detection
    shm.setRecordFlag(True)
    # Set the marker of objects on the image
    shm.setMarkFlag(True)
    # Set the flag running
    shm.setRunFlag(True)
    # Set the flag exit
    shm.setExitFlag(False)
    # Set the pipe flag
    shm.setPipeFlag(False)

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
