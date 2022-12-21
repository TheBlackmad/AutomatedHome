# AutomatedHome
Project for automated devices for home

This intend to integrate several devices such as lamps, temperature, humidity sensors, dehumidifiers, etc. into one system for monitor an control automatically.

Devices supported:

- Telegram (/telegram) provides a message sender. Message to send and recipient is given by the topic subscribed.
- Shelly devices (/shelly) for power control. It provided to published topics information about the status of the device, as well as receives commands through MQTT topics.

All modules connesct to an MQTT Broker to exchange messages. Events are triggered by update to the topics subscribed or published.

Next steps include monitor and control of Yeelight equipment, Dehumidifiers from Comfee, DIY sensors for temperature and humidifiers, notifications tool over Telegram and any other function that may be useful.
