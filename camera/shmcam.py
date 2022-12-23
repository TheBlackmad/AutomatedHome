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

import io
from multiprocessing import shared_memory
import threading
import cv2
import numpy as np
import logging

# Constants definition
MAX_SHM_ITEMS = 100
INDEX_BASE = 0
INDEX_IMAGE = INDEX_BASE + 0
INDEX_IMAGE_SHAPE = INDEX_BASE + 1
INDEX_IMAGE_FORMAT = INDEX_BASE + 2
INDEX_BOXES = INDEX_BASE + 3
INDEX_YOLO_FLAG = INDEX_BASE + 4
INDEX_RECORD_FLAG = INDEX_BASE + 5
INDEX_CAPTURE_FLAG = INDEX_BASE + 6
INDEX_VIEW_FLAG = INDEX_BASE + 7
INDEX_MARKER_FLAG = INDEX_BASE + 8
INDEX_PIPE_FLAG = INDEX_BASE + 9
INDEX_RUN_FLAG = INDEX_BASE + 10
INDEX_EXIT_FLAG = INDEX_BASE + 11

# Semaphore for accesing resources: image data
sem_image = threading.Semaphore(1)
sem_boxes = threading.Semaphore(1)

class SHMCAM:
    '''
        This class represents the access to a shared memory area where all other modules
        such as capture, view, recording can access to perform their jobs.
    '''

    def __init__(self, create=False, name=None, maxImageWidth=1920, maxImageHeight=1080, maxImageDepth=3, maxBoxes=100):
        '''
            This routine initializes the object shared memory.

            Args:
                create (bool): create the share memory (True) or access an existing one
                name (str): name of the shared memory block
                maxImageWidth (int): space for the image width in pixels
                maxImageHeight (int): space for the image height in pixels
                maxImageDepth (int): depth of the image stored (3 for RGB)
                maxBoxes (int): number of objects that can be identified in the image

            Returns:
                shared memory object

            Raises:
                None
        '''
        self._shm = None
        self.maxBoxes = maxBoxes
        self.maxImageWidth = maxImageWidth
        self.maxImageHeight = maxImageHeight
        self.maxImageDepth = maxImageDepth

        # if we need to create the Shared Memory space
        if create:

            # Create space for the variables
            image = b'\x00' * maxImageWidth * maxImageHeight * maxImageDepth # maximum size that can the image be
            imageShape = "({v1:d}, {v2:d}, {v3:d})".format(v1=maxImageWidth, v2=maxImageHeight, v3=maxImageDepth)
            imageFormat = "RGB24" #"This is the test Format"
            itemBox = "[ [ XXXX, YYYY, WWWW, HHHH ], 'This is the label of the box to display', 'This is the color of the label' ], "
            boxes = "[ " + " " * len(itemBox) * maxBoxes + " ]"
            yoloFlag = False
            recordFlag = False
            captureFlag = False
            viewFlag = False
            markerFlag = False  # Flag to allow marking the image as post processing from YOLO.
            pipeFlag = False
            runFlag = False
            exitFlag = False

            # Populate the list to be shareable
            sList = [ 0 ] * MAX_SHM_ITEMS
            sList[INDEX_IMAGE] = image
            sList[INDEX_IMAGE_SHAPE] = imageShape
            sList[INDEX_IMAGE_FORMAT] = imageFormat
            sList[INDEX_BOXES] = boxes
            sList[INDEX_YOLO_FLAG] = yoloFlag
            sList[INDEX_RECORD_FLAG] = recordFlag
            sList[INDEX_CAPTURE_FLAG] = captureFlag
            sList[INDEX_VIEW_FLAG] = viewFlag
            sList[INDEX_MARKER_FLAG] = markerFlag
            sList[INDEX_PIPE_FLAG] = pipeFlag
            sList[INDEX_RUN_FLAG] = runFlag
            sList[INDEX_EXIT_FLAG] = exitFlag

            if name is None:
                # this is the list for the Shared Memory
                self._shm = shared_memory.ShareableList(sList)
            else:
                # this is the list for the Shared Memory
                self._shm = shared_memory.ShareableList(sList, name=name)

            # after creation, initialize boxes to [ ]
            self.setBoxes([])
            self.setImageShape((maxImageWidth, maxImageHeight, maxImageDepth))
            self.setImageFormat('RGB24')

        # attach to existing one
        else:
            self._shm = shared_memory.ShareableList(name=name)

    def getImage(self):
        '''
            This routine gets image. Image is stored as serialized bytes

            Args:
                None

            Returns:
                image stored in shared memory

            Raises:
                None
        '''
        imageCorrect = False
        i=0

        sem_image.acquire()
        while not imageCorrect:
            img = np.frombuffer(self._shm[INDEX_IMAGE], dtype=np.uint8)
            shape = self.getImageShape()
            imageCorrect = (img.size * img.itemsize == shape[0] * shape[1] * shape[2])

        img = np.reshape(img, newshape=(shape[1], shape[0], shape[2]))
        sem_image.release()
        return img

    def getImageShape(self):
        '''
            This routine gets image shape.

            Args:
                None

            Returns:
                image shape

            Raises:
                None
        '''

        return eval(self._shm[INDEX_IMAGE_SHAPE])

    def getImageFormat(self):
        '''
            This routine gets image format.

            Args:
                None

            Returns:
                image shape

            Raises:
                None
        '''
        return self._shm[INDEX_IMAGE_FORMAT]
    
    def getBoxes(self):
        '''
            This routine gets objects in the image stored.

            Args:
                None

            Returns:
                image shape

            Raises:
                None
        '''
        sem_boxes.acquire()
        try:
            b = eval(self._shm[INDEX_BOXES])
        except Exception as e:
            logging.error(f"Exception when evaluating {self._shm[INDEX_BOXES]} *** " + str(e))
            b = []
        finally:
            sem_boxes.release()
        return b

    def getYoloFlag(self):
        '''
            This routine gets flag for allowing YOLO detector.

            Args:
                None

            Returns:
                value of Flag YOLO Detector

            Raises:
                None
        '''
        return self._shm[INDEX_YOLO_FLAG]
    
    def getRecordFlag(self):
        '''
            This routine gets flag for allowing recording.

            Args:
                None

            Returns:
                value of Flag Record

            Raises:
                None
        '''
        return self._shm[INDEX_RECORD_FLAG]
    
    def getCaptureFlag(self):
        '''
            This routine gets flag for allowing capturing.

            Args:
                None

            Returns:
                value of Flag Capture

            Raises:
                None
        '''
        return self._shm[INDEX_CAPTURE_FLAG]
    
    def getViewFlag(self):
        '''
            This routine gets flag for allowing display of image.

            Args:
                None

            Returns:
                value of Flag View

            Raises:
                None
        '''
        return self._shm[INDEX_VIEW_FLAG]
    
    def getMarkFlag(self):
        '''
            This routine gets flag for allowing marking image with object identification.

            Args:
                None

            Returns:
                value of Flag Mark

            Raises:
                None
        '''
        return self._shm[INDEX_MARKER_FLAG]
    
    def getPipeFlag(self):
        '''
            This routine gets flag for allowing image sent through a pipe.

            Args:
                None

            Returns:
                value of Flag Pipe

            Raises:
                None
        '''
        return self._shm[INDEX_PIPE_FLAG]
    
    def getRunFlag(self):
        '''
            This routine gets flag for allowing Running the programs.

            Args:
                None

            Returns:
                value of Flag Run

            Raises:
                None
        '''
        return self._shm[INDEX_RUN_FLAG]

    def getExitFlag(self):
        '''
            This routine gets flag for exit camera modules.

            Args:
                None

            Returns:
                value of Flag Exit

            Raises:
                None
        '''
        return self._shm[INDEX_EXIT_FLAG]

#
    #   IMAGE NEEDS TO BE OF A SPECIFIC FORMAT. IT IS PROBABLY BETTER TO HAVE A SPECIFIC FORMAT AS ENTRY.
    #
    def setImage(self, image, format):
        '''
            This routine set the image.

            Args:
                image (cv2 image): image to store in shared memory
                format (str): format of the image to store

            Returns:
                None

            Raises:
                None
        '''
        assert isinstance(image, np.ndarray)

        # the storage of the image is predefined.
        # if not the same shape, then resize
        # and turn to RGB24
        if format == 'yuv420p':
            conversion = cv2.COLOR_YUV420p2RGB
        elif format == 'yuyv422':
            conversion = cv2.COLOR_YUV2BGR_YUYV
        else:
            conversion = cv2.COLOR_YUV2BGR_YUYV
        img = cv2.cvtColor(image, conversion)
        shape = self.getImageShape()
        img = cv2.resize(img, (shape[0], shape[1]))

        sem_image.acquire()
        self._shm[INDEX_IMAGE] = img.tobytes()
        sem_image.release()

    def setImageShape(self, shape):
        '''
            This routine set the image shape.

            Args:
                shape (tuple): image to store in shared memory

            Returns:
                None

            Raises:
                None
        '''
        assert isinstance(shape, tuple)
        self._shm[INDEX_IMAGE_SHAPE] = str(shape)

    def setImageFormat(self, format):
        '''
            This routine set the image format.

            Args:
                format (str): format of the image to store

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_IMAGE_FORMAT] = format

    def setBoxes(self, boxes):
        '''
            This routine set the image.

            Args:
                boxes (list): list of boxes in form [ (x, y, w, h), label, color ]

            Returns:
                None

            Raises:
                None
        '''
        # Format of the alist should be as from the outcome of the YOLO Algorithm
        # [ [ [x, y, w, h], label, color], [[x, y, w, h], label, color], ... ]
        assert isinstance(boxes, list)
        sem_boxes.acquire()
        try:
            self._shm[INDEX_BOXES] = str(boxes)
        except Exception as e:
            logging.error(f"Exception when evaluating {boxes} *** " + str(e))
            self._shm[INDEX_BOXES] = "[]"
        finally:
            sem_boxes.release()

    def setYoloFlag(self, flag):
        '''
            This routine set the flag YOLO. It would allow the YOLO Detector modeule to
            run / not run

            Args:
                flag (bool): value for the flag

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_YOLO_FLAG] = flag

    def setRecordFlag(self, flag):
        '''
            This routine set the flag Record. It would allow the Record module to
            run / not run

            Args:
                flag (bool): value for the flag

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_RECORD_FLAG] = flag

    def setCaptureFlag(self, flag):
        '''
            This routine set the flag Capture. It would allow the Capture module to
            run / not run

            Args:
                flag (bool): value for the flag

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_CAPTURE_FLAG] = flag

    def setViewFlag(self, flag):
        '''
            This routine set the flag View. It would allow the View module to
            run / not run

            Args:
                flag (bool): value for the flag

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_VIEW_FLAG] = flag

    def setMarkFlag(self, flag):
        '''
            This routine set the flag Mark. It would allow the View module to
            display in the image the boxes of identified object or not

            Args:
                flag (bool): value for the flag

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_MARKER_FLAG] = flag

    def setPipeFlag(self, flag):
        '''
            This routine set the flag Pipe. It would allow the Capture module to
            send the image through a pipe or not.

            Args:
                flag (bool): value for the flag

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_PIPE_FLAG] = flag

    def setRunFlag(self, flag):
        '''
            This routine set the flag Run. It would allow all modules to
            run / not run

            Args:
                flag (bool): value for the flag

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_RUN_FLAG] = flag

    def setExitFlag(self, flag):
        '''
            This routine set the flag Exit. It would request all modules to
            exit and close

            Args:
                flag (bool): value for the flag

            Returns:
                None

            Raises:
                None
        '''
        self._shm[INDEX_EXIT_FLAG] = flag

    def close(self):
        '''
            This routine closes the access to the shared memory

            Args:
                None

            Returns:
                None

            Raises:
                None
        '''
        self._shm.shm.close()

    def unlink(self):
        '''
            This routine unlink the shared memory

            Args:
                None

            Returns:
                None

            Raises:
                None
        '''
        self._shm.shm.unlink()
