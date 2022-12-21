# AutomatedHome
Project for automated devices for home

This intend to integrate several devices such as lamps, temperature, humidity sensors, dehumidifiers, etc. into one system for monitor an control automatically.

First step is to integrate the interface through Telegram. the folder /telegram contains a telegram message sender.

Also, is included a module Shelly to interact with the Shelly devices, model S.

All modules connesct to an MQTT Broker to exchange messages. Events are triggered by update to the topics subscribed or published.

Next steps include monitor and control of Yeelight equipment, Dehumidifiers from Comfee, DIY sensors for temperature and humidifiers, notifications tool over Telegram and any other function that may be useful.
