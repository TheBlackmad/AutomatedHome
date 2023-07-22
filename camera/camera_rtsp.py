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
import gi
import threading
from threading import Thread

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

fps=25

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

# Sensor Factory class which inherits the GstRtspServer base class and add
# properties to it.
class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, shmid, **properties):
        super(SensorFactory, self).__init__(**properties)

        # Connect to area of shared memory to retrieve images
        logging.info(f"Connecting RTSP Server to shared memory with id: {shmid}")
        self.shm = shmcam.SHMCAM(create=False, name=shmid)

        self.shape = self.shm.getImageShape() # (width, height, depth)
        self.number_frames = 0
        self.fps = fps
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96' \
                             .format(self.shape[0], self.shape[1], self.fps)

    # method to capture the video feed from the camera and push it to the
    # streaming buffer.
    def on_need_data(self, src, length):

        t0 = time.time()
        try:
#            print(f"\nProviding a new image to stream through RTSP")
            frame = self.shm.getImage()

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
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label + ' ' + str(round(confidence*100)) + '%', (x, y - 10), font, 1 / 2, color, 2)

            # It is better to change the resolution of the camera
            # instead of changing the image shape as it affects the image quality.
##            data = frame.tostring()
            data = frame.tobytes()
            buf = Gst.Buffer.new_allocate(None, len(data), None)
            buf.fill(0, data)
            buf.duration = self.duration
            timestamp = self.number_frames * self.duration
            buf.pts = buf.dts = int(timestamp)
            buf.offset = timestamp
            self.number_frames += 1
            retval = src.emit('push-buffer', buf)
#            print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames, self.duration, self.duration / Gst.SECOND))
            if retval != Gst.FlowReturn.OK:
                logging.warning(f"Error streaming frame {self.number_frames} with errno {retval}")
            else:
#                print(f"Image provided correctly")
#                logging.info(f"Image provided correctly")
                pass
        except Exception as e:
            logging.warning(f"Something went wrong while streaming RTSP with error: {e}")

#        print(f"Time spent in sending a frame: {time.time()-t0}")

    # attach the launch string to the override method
    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)
    
    # attaching the source element to the rtsp media
    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)

# Rtsp server implementation where we attach the factory sensor with the stream uri
class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, shmid, uri, port, **properties):
        super(GstServer, self).__init__(**properties)
        self.factory = SensorFactory(shmid)
        self.factory.set_shared(True)
        self.set_service(str(port))
        self.get_mount_points().add_factory(uri, self.factory)
        self.attach(None)


if __name__ == "__main__":

    # interim hardcoded, what will change for coping with several camaras.
    uri = "/video"
    port = 6666

    # Check args input
    if len(sys.argv) != 2:
        print(f"An argument indicating the config file for the camera needs to be given.")
        exit(0)

    # Collecting data from the Logging File
    try:
        log = config(filename=sys.argv[1], section='logging')
    except Exception as e:
        print(f"Error reading the logfile: {str(e)}")
        exit(0)
    logfile=log["rtsp_logfile"]

    # Preparing the logging and metrics
    logging.basicConfig(filename=logfile, format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("Program started")
    metrics = timeMetrics.timeMetrics()

    try:
        cam_addr = config(filename=sys.argv[1], section='cam_addr')
    except Exception as e:
        logging.error(f"Error reading the source: {str(e)}")
        exit(0)
    camera_id = cam_addr["camera_id"]
    rtsp_server = eval(cam_addr["rtsp_server"])

    # check if it needs to run otherwise quit
    if not rtsp_server:
        exit(0)

    # Create area of shared memory
    logging.info(f"Connecting to shared memory with id: {camera_id}")
    shm = shmcam.SHMCAM(create=False, name=camera_id)

    # prepare RTSP Server creating thread for that if need to stream 
    # in some cases the camera is provided RTSP Streaming automatically
    logging.info("Starting thread for the RTSP Server")

    # wait for initialization time
    time.sleep(5)

    # initializing the threads and running the stream on loop.
###    GObject.threads_init()
    Gst.init(None)
    server = GstServer(camera_id, uri, port)
    loop = GObject.MainLoop()
    loop.run()

    # Disconnecting from the Shared Memory
    shm.close()


