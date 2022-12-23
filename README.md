# AutomatedHome
Project for automated devices for home

This intend to integrate several devices such as lamps, temperature, humidity sensors, dehumidifiers, etc. into one system for monitor an control automatically.

Devices supported:

- Telegram (/telegram) provides a message sender. Message to send and recipient is given by the topic subscribed.
- Shelly devices (/shelly) for power control. It provided to published topics information about the status of the device, as well as receives commands through MQTT topics.
- RTSP Camera (/camera) provides support to a camera system. The system is formed of several modules: main, capture, view, detector, recording. This permits connect to a camera, and detect persons through the YOLOv3 algorithm. This algorithm needs to bedownloaded from YOLO website and store the model under yolo-coco folder.

All modules connesct to an MQTT Broker to exchange messages. Events are triggered by update to the topics subscribed or published.

Next steps include monitor and control of Yeelight equipment, Dehumidifiers from Comfee, DIY sensors for temperature and humidifiers, notifications tool over Telegram and any other function that may be useful.
