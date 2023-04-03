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

import cv2
import torch
import imutils
import time
import numpy as np

#yolov3_weights = "./yolo-coco/ultralytics-yolov3-d1a1ea2/weights/weights/yolov3-tiny.weights"
#yolov3_config = "./yolo-coco/ultralytics-yolov3-d1a1ea2/cfg/yolov3-tiny.cfg"
##yolov3_weights = "./yolo-coco/ultralytics-yolov3-d1a1ea2/weights/weights/yolov3.weights"
##yolov3_config = "./yolo-coco/ultralytics-yolov3-d1a1ea2/cfg/yolov3.cfg"
#yolov3_coconames = "./yolo-coco/ultralytics-yolov3-d1a1ea2/data/coco.names"


class YOLO_Detector:
    '''
        This class intends to create an object detector based on the YOLOv3
        trained model.

        The code used in this library is mostly taken from
        https://www.codespeedy.com/yolo-object-detection-from-image-with-opencv-and-python/
    '''

    def __init__(self, path="ultralytics/yolov5", model="yolov5s"):
        '''
             This routine creates the neural network for using as object detector.

             Args:
                 None

             Returns:
                 A class Detector

             Raises:
                 None
        '''

        # Pytorch model
        self.model = torch.hub.load(path, model)

        print("(YOLO_Detector) YOLO loaded")

    def getPersons(self):
        '''
            This routine provides the number of persons identified in the
            last image retrieved.

            Args:
                None

            Returns:
                number of persons in the last frame retrieved

            Raises:
                None
        '''
        return self.numPersons

    def detect(self, img, confidence=0.65):
        ret = []
        color = 2128
        self.numPersons = 0

        results = self.model(img)
        p = results.pandas().xyxy[0]
        for i in range(len(p)):
            if p['confidence'][i] > confidence:
                if p['name'][i] == 'person':
                    ret.append([
                        [round(p['xmin'][i]),
                         round(p['ymin'][i]),
                         round(p['xmax'][i]-p['xmin'][i]),
                         round(p['ymax'][i]-p['ymin'][i])],
                        p['name'][i],
                        round(p['confidence'][i], 2),
                        color
                    ])
                    self.numPersons += 1

        return ret
