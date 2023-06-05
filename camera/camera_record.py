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
#import av
import queue
import time
from datetime import datetime
import threading
from threading import Thread
import signal
import shmcam
import timeMetrics
from configparser import ConfigParser

from fysom import Fysom

path_recording = None

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

# this function decides whether writing a video is required or not
def recordVideo(detected):
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
    global path_recording
    record = False
    value = False
    if detected > 0:
        value = True

    # if static variables are not initialized at the start, then do it
    if not hasattr(recordVideo, "buffer"):
        recordVideo.buffer = [False] * 1  # window to avoid spurious detections. valid detection is with all values True
    if not hasattr(recordVideo, "endRecord"):
        recordVideo.endRecord = 0.0  # when the record finishes
    if not hasattr(recordVideo, "filename"):
        recordVideo.filename = None  # it keeps the name of the filename during active recording

    # register time now
    jetzt = datetime.now()
    ts = datetime.timestamp(jetzt)

    # update buffer with the value True/False of detected person
    recordVideo.buffer.pop()
    recordVideo.buffer.insert(0, value)

    # if all buffer is positive finding person
    check = all(recordVideo.buffer)
    if check:
        # if a new video is required (i.e. the last endRecord is in the past)
        # then a new filename is to be created
        if recordVideo.endRecord < ts:
            recordVideo.filename = path_recording + "/record-" + str(jetzt.strftime("%Y-%m-%d_%H_%M_%S")) + ".avi"
        recordVideo.endRecord = ts + 10  # seconds

    # if record, then write the frame
    if ts < recordVideo.endRecord:
        record = True
    else:
        # leave record to False and return name of file to close if needed
        if recordVideo.filename != None:
            recordVideo.filename = None

    return record, recordVideo.filename

def writeVideo():
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
        img = framesRecordQueue.get()

        # if marker active then write boxes of obkject detection
        if shm.getMarkFlag():
            boxes = shm.getBoxes()
            for box in boxes:
                # font = cv2.FONT_HERSHEY_PLAIN
                font = cv2.FONT_HERSHEY_SIMPLEX
                x, y, w, h = box[0]
                label = box[1]
                confidence = box[2]
                color = 124 #box[2]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label + ' ' + str(round(confidence*100)) + '%', (x, y - 10), font, 1 / 2, color, 2)

        if out is not None:
            out.write(img)

        if fsm.isstate('exit'):
            break

def readFrames():
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
    while True:

        try:
            sig = signal.sigwait([SIGNALNR])
            handle = signal.getsignal(sig)
            handle(sig, None)
#            print("(ReadFrames) SIGNAL RECEVIED ON: ", time.time())

            if fsm.isstate('recording'):
                frame = shm.getImage()
                framesReadQueue.put(frame)

            if fsm.isstate('exit'):
                break

        except Exception as e:
            print("ERROR EXCEPTION READ!" + str(e))


def handler(sig_num, curr_stack_frame):
    '''
        This routine is handling signals (not use)

        Args:
            signum (int): signal number
            curr_stack_frame (object): caller

        Returns:
            None

        Raises:
            None
    '''
#    logging.info("Signal : '{}' Received. Handler Executed @ {}".format(signal.strsignal(sig_num), datetime.now()))
    pass

def createEvents():
    '''
        This routine creates the event of the state machine and changes the state as required.

        Args:
            None

        Returns:
            list of events for the state machine

        Raises:
            None
    '''
    global record, fn

    eventList = []

    # Events has a priority to be executed whenever it is possible. Lower number, higher priority.
    # It is in the form of a tuple (PRIO, EVENT)
    if shm.getExitFlag():   # need to exit
        eventList.append((0, 'exit'))
    else:   # if exit is False, do nothing
        pass

    if shm.getRunFlag():
        eventList.append((1, 'run'))
    else:
        eventList.append((1, 'norun'))

    if shm.getRecordFlag():
        eventList.append((2, 'record'))
    else:
        eventList.append((2, 'norecord'))

    # See the number of items detected
    objects = shm.getBoxes()
    record, fn = recordVideo(len(objects))
    if record:
        eventList.append((3, 'saverec'))
    else:
        eventList.append((3, 'saverecend'))

    return eventList


def createfile(e):
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
    global out, fn, writtenFrames, timeRecordStart, shm

#    print("CREATING THE VIDEO FILE")
    shape= shm.getImageShape()
    out = cv2.VideoWriter(fn, cv2.VideoWriter_fourcc(*'MPEG'), fps, (shape[0], shape[1]))

    writtenFrames = 0
    timeRecordStart = time.time()

def queueframe(e):
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
    global framesRecordQueue
    global framesReadQueue
    global record, fn, writtenFrames, image

    # get frames from the read queue and put it into the record queue.
    # if no frame is available from the read queue, put the last one.
    try:
        image = framesReadQueue.get(block=False)
    except queue.Empty as e:
#        print("EMPTY QUEUE!")
#        image = image
        pass

    try:
        framesRecordQueue.put(image, block=False)
    except queue.Full as e:
        pass

    writtenFrames += 1

def closefile(e):
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
    global out

    print("\nCLOSE THE VIDEO FILE")
    print(f"Time Recording is {time.time()-timeRecordStart}")
    while not framesRecordQueue.empty():
        time.sleep(0.1)
    out.release()
    print("Recording finished")


if __name__ == "__main__":
    SIGNALNR = 63

    nSamples = 0
    tAverage = 0.0
    tMax = 0.0
    writtenFrames = 0
    timeRecordStart = 0.0
    fps = 8
    input_stream = None

    record = False
    recording = False
    out = None
    framesRecordQueue = None
    framesReadQueue = None
    image = None
    shm = None      # shared memory area
    fsm = None      # Finite state machine

    fsm = Fysom( {
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
            'onenterrecording': createfile,
            'onreenterrecording': queueframe,
            'onleaverecording': closefile
        }
    })

    print(f"Current state: {fsm.current}")

    # Preparing the logging
    logging.basicConfig(format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("Program started")
    metrics = timeMetrics.timeMetrics()

    # Collecting data from the recording
    try:
        db = config(filename='camera.ini', section='recording')
    except Exception as e:
        print(f"Error reading the source: {str(e)}")
        exit(0)
    path_recording = db["path"]
    print(f"Reading video stream from {path_recording}")

    # Create area of shared memory
    shm = shmcam.SHMCAM(create=False, name="CAMERA_SHMEM")

    # Creating queue for the processing of frames
    framesRecordQueue = queue.Queue(1000)
    framesReadQueue = queue.Queue(1000)

    signal.signal(SIGNALNR, handler)

    # Create thread for reading frames
    logging.info("Starting thread reading frames")
    threadRecord = Thread(target=readFrames, args=())
    threadRecord.start()

    # Create thread for recording
    logging.info("Starting thread writing video")
    threadRecord = Thread(target=writeVideo, args=())
    threadRecord.start()

    time0 = time.time()
    nextRecordTime = 0

    while True:
        metrics.newCycle()
        nextRecordTime = time.time() + (1/fps)

        try:
            # execute every event
            events = createEvents()
            for e in events:
                if fsm.can(e[1]):
                    exe ='fsm.' + e[1] + '()'
                    eval(exe)

            for thread in threading.enumerate():
                signal.pthread_kill(thread.ident, SIGNALNR)

            sleeptime = nextRecordTime - time.time()
            if sleeptime < 0.0:
                sleeptime = 0.0
            time.sleep(sleeptime)
        #    print(f"Start Time: {start}\t Next record time: {nextRecordTime}\t Sleep Time: {sleeptime}")

        except Exception as e:
            print("EXCEPTION: ", str(e))

        # Calculate metrics
        print(f"\r{metrics.endCycle().toString()}", end="", flush=True)

    logging.info("Exiting view program")
    shm._shm.close()
    shm._shm.unlink()
