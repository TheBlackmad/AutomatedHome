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
import skvideo.io
import queue
import time
from datetime import datetime
import threading
from threading import Thread
import signal
import shmcam
import timeMetrics
from configparser import ConfigParser
import sys

from fysom import Fysom


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


#def handler(sig_num, curr_stack_frame):
#    '''
#        This routine is handling signals (not use)
#
#        Args:
#            signum (int): signal number
#            curr_stack_frame (object): caller
#
#        Returns:
#            None
#
#        Raises:
#            None
#    '''
#    logging.info("Signal : '{}' Received. Handler Executed @ {}".format(signal.strsignal(sig_num), datetime.now()))
#    pass


class Recorder():

    def __init__(self, shm, path_recording):

#        self.SIGNALNR = 63

        # variables for statistics and calculations
        self.path_recording = path_recording
        self.writtenFrames = 0
        self.timeRecordStart = 0.0
#        self.nextRecordTime = 0
        self.fps = 8

        self._rvBuffer = [False] * 1  # window to avoid spurious detections. valid detection is with all values True
        self._rvEndrecord = 0.0       # when the record finishes

        # objects 
        self.record = False
        self.out = None
        self.image = None
        self.fn = None                # it keeps the name of the filename during active recording

        # Finite state machine of the recorder
        self.fsm = Fysom( {
            'initial': 'init',
            'final': 'return',
            'events': [
                {'name': 'run', 'src': [ 'init', 'running' ], 'dst': 'running'},
                {'name': 'norun', 'src': [ 'init', 'running' ], 'dst': 'init'},
                {'name': 'exit', 'src': [ 'init', 'running' ], 'dst': 'return'},
                {'name': 'record', 'src': [ 'running', 'recordingready' ], 'dst': 'recordingready'},
                {'name': 'saverec', 'src': [ 'recordingready', 'recording' ], 'dst': 'recording'},
                {'name': 'saverecend', 'src': 'recording', 'dst': 'recordingready'},
                {'name': 'norecord', 'src': 'recording', 'dst': 'running'},
            ],
            'callbacks': {
                'onenterrecording': self.createfile,
                'onreenterrecording': self.queueframe,
                'onleaverecording': self.closefile
            }
        })

        # Reference to the shared memory area
        self.shm = shm

        # Creating queue for the processing of frames
        self.framesRecordQueue = queue.Queue(1000)
        self.framesReadQueue = queue.Queue(1000)

        # Create thread for reading frames
#        logging.info("Starting thread reading frames")
#        threadRead = Thread(target=readFrames, args=())
#        threadRead.start()

        # Create thread for recording
        logging.info("Starting thread writing video")
        threadRecord = Thread(target=self.writeVideo, args=())
        threadRecord.start()

        # signal 
#        signal.signal(self.SIGNALNR, handler)


    def loop_run(self):

        nextRecordTime = time.time() + (1/self.fps)

        try:
            # execute every event
            events = self.createEvents()
            for e in events:
                if self.fsm.can(e[1]):
                    exe ='self.fsm.' + e[1] + '()'
                    eval(exe)

            # process frames at the loop frequency
#            for thread in threading.enumerate():
#                signal.pthread_kill(thread.ident, SIGNALNR)
            self.readFrames()

            sleeptime = nextRecordTime - time.time()
            if sleeptime < 0.0:
                sleeptime = 0.0
            time.sleep(sleeptime)
#            print(f"Start Time: {start}\t Next record time: {nextRecordTime}\t Sleep Time: {sleeptime}")

        except Exception as e:
            logging.error("EXCEPTION: ", str(e))


    # this function decides whether writing a video is required or not
    def recordVideo(self, detected):
        '''
            This routine decides whether writing a video is needed or not. It takes a buffer of
            images and if all the images in the buffer identifies an object, then sets the flag.
            The flag will be set for at least 10 seconds after no object is detected anymore.

            Args:
                detected (int): number of objects detected

            Returns:
                record (bool): flag that signals whether to record or not.
                filename (str): filename to be use in the recording.

            Raises:
                None
        '''

        value = False
        if detected > 0:
            value = True

        # register time now
        jetzt = datetime.now()
        ts = datetime.timestamp(jetzt)

        # update buffer with the value True/False of detected person
        self._rvBuffer.pop()
        self._rvBuffer.insert(0, value)

        # if all buffer is positive finding person
        check = all(self._rvBuffer)
        if check:
            # if a new video is required (i.e. the last endRecord is in the past)
            # then a new filename is to be created
            if self._rvEndrecord < ts:
                self.fn = self.path_recording + "record-" + str(jetzt.strftime("%Y-%m-%d_%H_%M_%S")) + ".avi"
            self._rvEndrecord = ts + 10  # seconds

        # if record, then write the frame
        if ts < self._rvEndrecord:
            self.record = True
        else:
            # leave record to False and return name of file to close if needed
            self.record = False
            if self.fn != None:
                self.fn = None

        return self.record, self.fn


    def writeVideo(self):
        '''
            This routine is thought to run as a thread as is in charge of waiting
            for a signal to run. the frequency at which it runs is commanded from
            outside this routine.
            If there is any frame in the RECORD QUEUE, it writes it to the file.
            The written image will include as well the Boxes identifying boxes if
            the MARK FLAG is set.

            Args:
                None

            Returns:
                None

            Raises:
                None
        '''

        while True:
            # get the frame and write
            img = self.framesRecordQueue.get()

            # if marker active then write boxes of object detection
            if self.shm.getMarkFlag():
                boxes = self.shm.getBoxes()
                for box in boxes:
                    # font = cv2.FONT_HERSHEY_PLAIN
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    x, y, w, h = box[0]
                    label = box[1]
                    confidence = box[2]
                    color = 124 #box[2]
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(img, label + ' ' + str(round(confidence*100)) + '%', (x, y - 10), font, 1 / 2, color, 2)

            if self.out is not None:
                self.out.write(img)

            if self.fsm.isstate('exit'):
                break


    def readFrames(self):
        '''
            This routine is thought to run as a thread as is in charge of waiting
            for a signal to run. the frequency at which it runs is commanded from
            outside this routine.
            If the state machine is recording, it queues from shared memory the
            image into the READ QUEUE.

            Args:
                None

            Returns:
                None

            Raises:
                None
        '''
        t0 = time.time()
        try:
#            sig = signal.sigwait([self.SIGNALNR])
#            handle = signal.getsignal(sig)
#            handle(sig, None)

            if self.fsm.isstate('recording'):
                frame = self.shm.getImage()
                self.framesReadQueue.put(frame)

        except Exception as e:
            logging.error("ERROR EXCEPTION READ!" + str(e))


    def createEvents(self):
        '''
            This routine creates the event of the state machine and changes the state as required.

            Args:
                None

            Returns:
                list of events for the state machine

            Raises:
                None
        '''

        eventList = []

        # Events has a priority to be executed whenever it is possible. Lower number, higher priority.
        # It is in the form of a tuple (PRIO, EVENT)
        if self.shm.getExitFlag():   # need to exit
            eventList.append((0, 'exit'))
        else:   # if exit is False, do nothing
            pass

        if self.shm.getRunFlag():
            eventList.append((1, 'run'))
        else:
            eventList.append((1, 'norun'))

        if self.shm.getRecordFlag():
            eventList.append((2, 'record'))
        else:
            eventList.append((2, 'norecord'))

        # See the number of items detected
        objects = self.shm.getBoxes()
        self.record, self.fn = self.recordVideo(len(objects))
        if self.record:
            eventList.append((3, 'saverec'))
        else:
            eventList.append((3, 'saverecend'))

        return eventList


    def createfile(self, e):
        '''
            This routine creates a new record file. When the state is create a new movie
            this routine is doing exactly that.

            Args:
                e (event): event generated from the state machine

            Returns:
                None

            Raises:
                None
        '''

        logging.info(f"Creating new video file")
        shape = self.shm.getImageShape()
        self.out = cv2.VideoWriter(self.fn, cv2.VideoWriter_fourcc(*'MPEG'), self.fps, (shape[0], shape[1]))

        self.writtenFrames = 0
        self.timeRecordStart = time.time()


    def queueframe(self, e):
        '''
            This routine queues a new frame into the Record Queue. The frame is
            retrieved from the Read Queue.

            Args:
                e (event): event

            Returns:
                list of boxes where the persons where identified

            Raises:
                None
        '''

        # get frames from the read queue and put it into the record queue.
        # if no frame is available from the read queue, put the last one.
        try:
            self.image = self.framesReadQueue.get(block=False)
        except queue.Empty as e:
#            print("EMPTY QUEUE!")
#            self.image = self.image
            pass

        try:
            self.framesRecordQueue.put(self.image, block=False)
        except queue.Full as e:
            pass

        self.writtenFrames += 1


    def closefile(self, e):
        '''
            This routine close the recording file as it is no longer needed to
            file a movie.

            Args:
                e (event): event

            Returns:
                None

            Raises:
                None
        '''

        # Recording is finished. However, when the record queue is empty, the write process needs to 
        # write the last frame to the file. We need to ensure that this process is giving time to write
        # the last frame to the file. Thus, 1 sec to complete.
        logging.info(f"New video file recorded. Recording time is {time.time()-self.timeRecordStart}")
        while not self.framesRecordQueue.empty():
            time.sleep(0.1)
        time.sleep(1)
        self.out.release()



if __name__ == "__main__":    

    # Collecting data from the config file
    try:
        db = config(filename=sys.argv[1], section='logging')
    except Exception as e:
        print(f"Error reading the source: {str(e)}")
        exit(0)
    logfile = db["record_logfile"]

    # Preparing the logging
    logging.basicConfig(filename=logfile, format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("Program started")
    metrics = timeMetrics.timeMetrics()

    # Collecting data from the recording
    try:
        dbr = config(filename=sys.argv[1], section='recording')
    except Exception as e:
        print(f"Error reading the source: {str(e)}")
        exit(0)
    print(f"Setting directory for storing recordings to {dbr['path']}")

    # Collecting data from the camera memory
    try:
        dbc = config(filename=sys.argv[1], section='cam_addr')
    except Exception as e:
        print(f"Error reading the source: {str(e)}")
        exit(0)

    # Create area of shared memory
    shm = shmcam.SHMCAM(create=False, name=dbc['camera_id'])

    # Create the object recorder
    recorder = Recorder(shm, dbr['path'])
    logging.info(f"Current state: {recorder.fsm.current}")
    previous_state = recorder.fsm.current

    while True:
        metrics.newCycle()

        recorder.loop_run()
        if previous_state != recorder.fsm.current:
            logging.info(f"Recorder now in state: {recorder.fsm.current}.")
            previous_state = recorder.fsm.current

        # Calculate metrics
        print(f"\r{metrics.endCycle().toString()}", end="", flush=True)

    logging.info("Exiting view program")
    shm._shm.close()
    shm._shm.unlink()
