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
import imutils
import time
import numpy as np

yolov3_weights = "./yolo-coco/ultralytics-yolov3-d1a1ea2/weights/weights/yolov3-tiny.weights"
yolov3_config = "./yolo-coco/ultralytics-yolov3-d1a1ea2/cfg/yolov3-tiny.cfg"
#yolov3_weights = "./yolo-coco/ultralytics-yolov3-d1a1ea2/weights/weights/yolov3.weights"
#yolov3_config = "./yolo-coco/ultralytics-yolov3-d1a1ea2/cfg/yolov3.cfg"
yolov3_coconames = "./yolo-coco/ultralytics-yolov3-d1a1ea2/data/coco.names"


class YOLO_Detector:
    '''
        This class intends to create an object detector based on the YOLOv3
        trained model.

        The code used in this library is mostly taken from
        https://www.codespeedy.com/yolo-object-detection-from-image-with-opencv-and-python/
    '''

    def __init__(self):
        '''
            This routine creates the neural network for using as object detector.

            Args:
                None

            Returns:
                A class Detector

            Raises:
                None
        '''
        self.net = None
        self.classes = []
        self.layer_names = None
        self.output_layers = None
        self.numPersons = 0

        # Load Yolo
        print(f"YOLO Weights: {yolov3_weights}\nYOLO Config: {yolov3_config}\nYOLO Coco.names: {yolov3_coconames}")
        print("(YOLO_Detector) Loading YOLO . . .")
        self.net = cv2.dnn.readNet(yolov3_weights, yolov3_config)
        # save all the names in file o the list classes
        self.classes = []
        with open(yolov3_coconames, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        # get layers of the network
        self.layer_names = self.net.getLayerNames()
        # Determine the output layer names from the YOLO model
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
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

    def detectObjects(self, img):
        '''
            This routine identifies persons in the image given as argument

            Args:
                img (cv2 image): image where to identify persons

            Returns:
                list of boxes where the persons where identified

            Raises:
                None
        '''
        try:
            height, width, channels = img.shape

            # USing blob function of opencv to preprocess image
#            blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416),  swapRB=True, crop=False)
            blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (224, 224), swapRB=True, crop=False)

            # Detecting objects
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)
            # Showing informations on the screen
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        # Object detected
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # We use NMS function in opencv to perform Non-maximum Suppression
            # we give it score threshold and nms threshold as arguments.
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            #        font = cv2.FONT_HERSHEY_PLAIN
            font = cv2.FONT_HERSHEY_SIMPLEX
            colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
            self.numPersons = 0
            ret = []
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    if self.classes[class_ids[i]] == "person":
                        self.numPersons += 1

                    label = str(self.classes[class_ids[i]])
#                    color = colors[class_ids[i]]
#                    color = (64, 64, 255)
                    color = 2128
#                    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
#                    cv2.putText(img, label, (x, y + 30), font, 1 / 2, color, 2)

                    # what if we return the boxes instead of the frames???
                    print("***** ", [[x, y, w, h], label, color])
                    ret.append([[x, y, w, h], label, color])

        except AttributeError as ae:
            print(ae)

        return ret
