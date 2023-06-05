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
import platform
import numpy as np

# decice tree for rk356x/rk3588
DEVICE_COMPATIBLE_NODE = '/proc/device-tree/compatible'

class YOLO_Detector:
    '''
        This class intends to create an object detector based on the YOLOv3
        trained model. The model can run on a Linux based system, but also on a Rockchip 356X/3588
        with NPU.

        The code used in this library is based on
        https://www.codespeedy.com/yolo-object-detection-from-image-with-opencv-and-python/
        https://github.com/rockchip-linux/rknn-toolkit2
    '''

    def __init__(self, path="ultralytics/yolov5", model="yolov5s", rknn_model="yolov5s.rknn"):
        '''
             This routine creates the neural network for using as object detector.

             Args:
                 None

             Returns:
                 A class Detector

             Raises:
                 None
        '''
        # initialize attributes
        self.host = None
        self.model = None
        self.rknn_lite = None
        self.IMG_SIZE = 640
        self.BOX_THESH = 0.5
        self.NMS_THRESH = 0.6
        self.CLASSES = ("person", "bicycle", "car", "motorbike ", "aeroplane ", "bus ", "train", "truck ", "boat", "traffic light",
           "fire hydrant", "stop sign ", "parking meter", "bench", "bird", "cat", "dog ", "horse ", "sheep", "cow", "elephant",
           "bear", "zebra ", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
           "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife ",
           "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza ", "donut", "cake", "chair", "sofa",
           "pottedplant", "bed", "diningtable", "toilet ", "tvmonitor", "laptop ", "mouse   ", "remote ", "keyboard ", "cell phone", "microwave ",
           "oven ", "toaster", "sink", "refrigerator ", "book", "clock", "vase", "scissors ", "teddy bear ", "hair drier", "toothbrush ")


        # machine in order to use NPU if available
        self.host = self.get_host()
        print(f"Host: {self.host}")
        
        # if the machine is a rockchip with NPU, in particular
        # a RK3588 or RK356X
        if self.host == 'RK3588' or self.host == 'RK356x':
            try:
                from rknnlite.api import RKNNLite
            except ImportError as e:
                raise Exception(f"Error: {e}")
            
            try:
                
                self.rknn_lite = RKNNLite()

                # load RKNN model
                print('--> Load RKNN model')
                ret = self.rknn_lite.load_rknn(rknn_model)
                if ret != 0:
                    raise Exception(f"Error loading the RKNN model. Error {ret}")
                print('done')

                # init runtime environment
                print('--> Init runtime environment')
                # run on RK356x/RK3588 with Debian OS, do not need specify target.
                if self.host == 'RK3588':
                    ret = self.rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)
                else:
                    ret = self.rknn_lite.init_runtime()
                if ret != 0:
                    raise Exception(f"Init runtime environment failed. Error {ret}")
                print('done')
            except Exception as e:
                print("CAgondios")
                raise Exception(e)
                
            print(f"(YOLO_Detector) YOLO loaded in NPU of {self.host}")
        
        # else in CPU   
        else:
        
            try:
            
                import torch
                
                # Pytorch model
                self.model = torch.hub.load(path, model)
                print("(YOLO_Detector) YOLO loaded")
            except Exception as e:
                raise Exception(e)

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
        ratio_x = 0.0
        ratio_y = 0.0


        if self.host == 'RK3588' or self.host == 'RK356x':
        
            # Set inputs
            # img, ratio, (dw, dh) = letterbox(img, new_shape=(IMG_SIZE, IMG_SIZE))
            try:
                frame = img
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.IMG_SIZE, self.IMG_SIZE))
                ratio_x = img.shape[1] / frame.shape[1]
                ratio_y = img.shape[0] / frame.shape[0]
            except Exception as e:
                print(f"Error resizing image for the object detection model")

            try:
                # Inference
                outputs = self.rknn_lite.inference(inputs=[frame])
            except Exception as e:
                print(f"Error while inference - {e}")
                
            try:

                # post process
                input0_data = outputs[0]
                input1_data = outputs[1]
                input2_data = outputs[2]

                input0_data = input0_data.reshape([3, -1]+list(input0_data.shape[-2:]))
                input1_data = input1_data.reshape([3, -1]+list(input1_data.shape[-2:]))
                input2_data = input2_data.reshape([3, -1]+list(input2_data.shape[-2:]))

                input_data = list()
                input_data.append(np.transpose(input0_data, (2, 3, 0, 1)))
                input_data.append(np.transpose(input1_data, (2, 3, 0, 1)))
                input_data.append(np.transpose(input2_data, (2, 3, 0, 1)))

                boxes, classes, scores = self.yolov5_post_process(input_data)
                for i in range(len(boxes)):
                    if scores[i] > confidence:
                        if self.CLASSES[classes[i]]  == 'person':
                            ret.append([
                                [round(boxes[i][0]*ratio_x),
                          round( boxes[i][1]*ratio_y ),
                             round( ratio_x*(boxes[i][2]-boxes[i][0]) ),
                             round( ratio_y*(boxes[i][3]-boxes[i][1]) )],
                            self.CLASSES[classes[i]],
                            round(scores[i], 2),
                            color
                        ])
                        self.numPersons += 1
                        
            except Exception as e:
                print(f"Error {e}")
        
        # else in CPU
        else:        
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
        
    def get_host(self):
        # get platform and device type
        system = platform.system()
        machine = platform.machine()
        os_machine = system + '-' + machine
        if os_machine == 'Linux-aarch64':
            try:
                with open(DEVICE_COMPATIBLE_NODE) as f:
                    device_compatible_str = f.read()
                    if 'rk3588' in device_compatible_str:
                        host = 'RK3588'
                    else:
                        host = 'RK356x'
            except IOError:
                print('Read device node {} failed.'.format(DEVICE_COMPATIBLE_NODE))
                exit(-1)
        else:
            host = os_machine
        
        return host
        
        
    def sigmoid(self,x):
        return 1 / (1 + np.exp(-x))

    def xywh2xyxy(self, x):
        # Convert [x, y, w, h] to [x1, y1, x2, y2]
        y = np.copy(x)
        y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
        y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
        y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
        y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
        return y

    def process(self, input, mask, anchors):

        anchors = [anchors[i] for i in mask]
        grid_h, grid_w = map(int, input.shape[0:2])

        box_confidence = self.sigmoid(input[..., 4])
        box_confidence = np.expand_dims(box_confidence, axis=-1)

        box_class_probs = self.sigmoid(input[..., 5:])

        box_xy = self.sigmoid(input[..., :2])*2 - 0.5

        col = np.tile(np.arange(0, grid_w), grid_w).reshape(-1, grid_w)
        row = np.tile(np.arange(0, grid_h).reshape(-1, 1), grid_h)
        col = col.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
        row = row.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
        grid = np.concatenate((col, row), axis=-1)
        box_xy += grid
        box_xy *= int(self.IMG_SIZE/grid_h)

        box_wh = pow(self.sigmoid(input[..., 2:4])*2, 2)
        box_wh = box_wh * anchors

        box = np.concatenate((box_xy, box_wh), axis=-1)

        return box, box_confidence, box_class_probs

    def filter_boxes(self, boxes, box_confidences, box_class_probs):
        """Filter boxes with box threshold. It's a bit different with origin yolov5 post process!

        # Arguments
            boxes: ndarray, boxes of objects.
            box_confidences: ndarray, confidences of objects.
            box_class_probs: ndarray, class_probs of objects.

        # Returns
            boxes: ndarray, filtered boxes.
            classes: ndarray, classes for boxes.
            scores: ndarray, scores for boxes.
        """
        box_classes = np.argmax(box_class_probs, axis=-1)
        box_class_scores = np.max(box_class_probs, axis=-1)
        pos = np.where(box_confidences[..., 0] >= self.BOX_THESH)

        boxes = boxes[pos]
        classes = box_classes[pos]
        scores = box_class_scores[pos]

        return boxes, classes, scores

    def nms_boxes(self, boxes, scores):
        """Suppress non-maximal boxes.

        # Arguments
            boxes: ndarray, boxes of objects.
            scores: ndarray, scores of objects.

        # Returns
            keep: ndarray, index of effective boxes.
        """
        x = boxes[:, 0]
        y = boxes[:, 1]
        w = boxes[:, 2] - boxes[:, 0]
        h = boxes[:, 3] - boxes[:, 1]

        areas = w * h
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x[i], x[order[1:]])
            yy1 = np.maximum(y[i], y[order[1:]])
            xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
            yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])

            w1 = np.maximum(0.0, xx2 - xx1 + 0.00001)
            h1 = np.maximum(0.0, yy2 - yy1 + 0.00001)
            inter = w1 * h1

            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(ovr <= self.NMS_THRESH)[0]
            order = order[inds + 1]
        keep = np.array(keep)
        return keep


    def yolov5_post_process(self, input_data):
        masks = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        anchors = [[10, 13], [16, 30], [33, 23], [30, 61], [62, 45],
                   [59, 119], [116, 90], [156, 198], [373, 326]]

        boxes, classes, scores = [], [], []
        for input, mask in zip(input_data, masks):
            b, c, s = self.process(input, mask, anchors)
            b, c, s = self.filter_boxes(b, c, s)
            boxes.append(b)
            classes.append(c)
            scores.append(s)

        boxes = np.concatenate(boxes)
        boxes = self.xywh2xyxy(boxes)
        classes = np.concatenate(classes)
        scores = np.concatenate(scores)

        nboxes, nclasses, nscores = [], [], []
        for c in set(classes):
            inds = np.where(classes == c)
            b = boxes[inds]
            c = classes[inds]
            s = scores[inds]

            keep = self.nms_boxes(b, s)

            nboxes.append(b[keep])
            nclasses.append(c[keep])
            nscores.append(s[keep])

        if not nclasses and not nscores:
#            return None, None, None
            return [], [], []

        boxes = np.concatenate(nboxes)
        classes = np.concatenate(nclasses)
        scores = np.concatenate(nscores)

        return boxes, classes, scores

