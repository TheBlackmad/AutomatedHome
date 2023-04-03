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
import av
import cv2
import time
import sys
import shmcam
import timeMetrics
from configparser import ConfigParser
from numpy import asarray

import YOLO_Detector as yolo

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

def isCameraIndex(path):
    assert isinstance(path, str)
    return path.isdigit()

pipe_name = 'video_pipe'
pipeout = None
nSamples = 0
tAverage = 0.0
tMax = 0.0

if __name__ == "__main__":
    # Preparing the logging and metrics
    logging.basicConfig(format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("Program started")
    metrics = timeMetrics.timeMetrics()

    # Collecting data from the Bank
    try:
        db = config(filename='camera.ini', section='cam_addr')
    except Exception as e:
        print(f"Error reading the source: {str(e)}")
        exit(0)
    path_video = db["camera_address"]
    print(f"Reading video stream from {path_video}")

    # Create area of shared memory
    shm = shmcam.SHMCAM(create=False, name="CAMERA_SHMEM")

    # Create the pipe communication
    if shm.getPipeFlag():
        try:
            logging.info("Open the communication pipe")
            if os.path.exists(pipe_name):
                os.remove(pipe_name)
            os.mkfifo(pipe_name)
            pipeout = open(pipe_name, "wb")
        except Exception as e:
            logging.error("Error Exception: " + str(e))

    # connect to the soure of video
    cap = None
    try:
        logging.info(f"Opening the video source {path_video}")
        if isCameraIndex(path_video):
            print(f"Opening device index: {path_video}")
            cap = cv2.VideoCapture(int(path_video))
        else:
            print(f"Opening device path: {path_video}")
            input_container = av.open(path_video)
            input_stream = input_container.streams.get(video=0)[0]
    except Exception as e:
        logging.error("EXCEPTION: " + str(e))
        exit(-1)

    # Wait until run flag is activated
    while not shm.getRunFlag():
        logging.info("Waiting ......")
        pass

    # retrieve each frame
    logging.info("Now capturing frames . . .")

    # The reason to use av is to support RTSP services. AV also supports paths
    # However av, does not support indexes for the cameras, at least in some computers.
    if not isCameraIndex(path_video):

        for frame in input_container.decode(input_stream):

            metrics.newCycle()

            if shm.getCaptureFlag() and shm.getRunFlag():
                try:

                    img = frame.to_ndarray(format=frame.format.name, width=frame.format.width, height=frame.format.height)

                    # make available to the external world
                    shm.setImage(img, frame.format.name)

                    # send to the pipe
                    if shm.getPipeFlag():
                        if pipeout is None:
                            try:
                                logging.info("Open the communication pipe")
                                if os.path.exists(pipe_name):
                                    os.remove(pipe_name)
                                os.mkfifo(pipe_name)
                                pipeout = open(pipe_name, "wb")
                            except Exception as e:
                                logging.error("Error Exception: " + str(e))
                        pickle_img = pickle.dumps(img)
                        logging.info(f"Sending image ({sys.getsizeof(img)} / {sys.getsizeof(pickle_img)}) to the PIPE {pipeout} \Data: {type(img)}")
                        pipeout.write(pickle_img)

                except Exception as e:
                    logging.error("ERROR EXCEPCIÓN: " + str(e))

            # need to quit?
            if shm.getExitFlag():
                break

            # Calculate metrics
            print(f"\r{metrics.endCycle().toString()}", end="", flush=True)

            time.sleep(1/25)

    # this is a camera index, only address supported by OpenCV
    else:

        while(True):

            metrics.newCycle()

            if shm.getCaptureFlag() and shm.getRunFlag():
                try:

                    ret, frame = cap.read()

                    # make available to the external world
                    if ret:
                        shm.setImage(frame, "rgb24")

                    # send to the pipe
                    if shm.getPipeFlag():
                        if pipeout is None:
                            try:
                                logging.info("Open the communication pipe")
                                if os.path.exists(pipe_name):
                                    os.remove(pipe_name)
                                os.mkfifo(pipe_name)
                                pipeout = open(pipe_name, "wb")
                            except Exception as e:
                                logging.error("Error Exception: " + str(e))
                        pickle_img = pickle.dumps(img)
                        logging.info(
                            f"Sending image ({sys.getsizeof(img)} / {sys.getsizeof(pickle_img)}) to the PIPE {pipeout} \Data: {type(img)}")
                        pipeout.write(pickle_img)

                except Exception as e:
                    logging.error("ERROR EXCEPCIÓN: " + str(e))

            # need to quit?
            if shm.getExitFlag():
                break

            # Calculate metrics
            print(f"\r{metrics.endCycle().toString()}", end="", flush=True)

            time.sleep(1 / 25)


    logging.info("Exiting capture program")
    if shm.getPipeFlag():
        os.close(pipeout)
        os.remove(pipe_name)

    # Disconnecting from the Shared Memory
    shm.close()
    input_container.close()


