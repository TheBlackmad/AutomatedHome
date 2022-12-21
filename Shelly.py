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

import time
import datetime
from datetime import date
import sys
import paho.mqtt.client as mqtt
import os

from configparser import ConfigParser
import logging

_FILE_LOG_SUFFIX_ = ".log"



def config(filename='config.cfg', section='section'):
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

    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    cfg = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            cfg[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return cfg


class Shelly:
    def __init__(self, topic, room, device, brokerIP='127.0.0.1', brokerPort=1883):
        '''
            This routine gets reads the config/init file using the
            library ConfigParser

            Args:
                topic (str): topic to subscribe to
                room (str): room associated to the device (location)
                device (str): device name
                brokerIP (str): IP address of the MQTT broker to connect to
                brokerPort (str): Port of the MQTT broker

            Returns:
                An object shelly

            Raises:
                None
        '''

        # Attributes of the object
        self.temperature = ""
        self.temperature_f = ""
        self.overtemperature = ""
        self.status = ""
        self.energy = ""
        self.announce = ""
        self.power = ""
        self.brokerIP = brokerIP
        self.brokerPort = brokerPort
        
        
        # Attributes of the topics
        self.deviceTopic = topic
        self.listenTopic = self.deviceTopic + "/#"
        self.automatedHomeTopic = "/" + room + "/" + device
        
        # Create connection to the MQTT Broker
        self.clientBroker = mqtt.Client()
        self.clientBroker.on_connect = self.on_connect
        self.clientBroker.on_message = self.on_message
        self.clientBroker.connect(brokerIP, brokerPort)
        
        logging.info("Connected to broker " + self.brokerIP + ":" + str(self.brokerPort))
        logging.info("Listen to device on MQTT Topic: " + self.listenTopic)
        

    # function on_connect for the mosquitto broker
    def on_connect(self, client, userdata, flags, rc):
        '''
        This routine is called when connected to the mosquitto broker

        Args:
            client: client object
            userdata: data referencing the originator
            flags: from the call
            rc: rc

        Returns:
            creates a connection to the topic. this is a callback to new connection

        Raises:
            Exception: when subcription to topic not possible
        '''
        logging.info("Connected with result code " + str(rc))
        
        try:
            # Subscribing in on_connect () means that if we lose the connection 
            # and reconnect then subscription will be renewed.
            client.subscribe(self.listenTopic, 0)
        except Exception as e:
            logging.error("EXCEPTION RAISED: " + str(e))
        

    # function on_message for the mosquitto broker
    def on_message(self, client, userdata, message):

        '''
        This routine is called when a message is received from the mosquitto broker

        Args:
            client: client object
            userdata: data referencing the originator
            message (str): message received

        Returns:
            None

        Raises:
            Exception: Receiving message
        '''


        logging.info(str(message.topic) + " MSG: " + str(message.payload) + " with QoS " + str(message.qos))
        
        try:
            if str(message.topic) == self.deviceTopic + "/temperature":
                if self.temperature != message.payload:
                    client.publish(self.automatedHomeTopic + "/temperature", message.payload)
                    self.temperature = message.payload
                
            elif str(message.topic) == self.deviceTopic + "/temperature_f":
                if self.temperature_f != message.payload:
                    client.publish(self.automatedHomeTopic + "/temperature_f", message.payload)
                    self.temperature_f = message.payload
                
            elif str(message.topic) == self.deviceTopic + "/overtemperature":
                if self.overtemperature != message.payload:
                    client.publish(self.automatedHomeTopic + "/overtemperature", message.payload)
                    self.overtemperature = message.payload
                
            elif str(message.topic) == self.deviceTopic + "/relay/0":
                if self.status != message.payload:
                    client.publish(self.automatedHomeTopic + "/status", message.payload)
                    self.status = message.payload
                
            elif str(message.topic) == self.deviceTopic + "/relay/0/power":
                if self.power != message.payload:
                    client.publish(self.automatedHomeTopic + "/power", message.payload)
                    self.power = message.payload
                
            elif str(message.topic) == self.deviceTopic + "/relay/0/energy":
                if self.energy != message.payload:
                    client.publish(self.automatedHomeTopic + "/energy", message.payload)
                    self.energy = message.payload
                
            elif str(message.topic) == self.deviceTopic + "/announce":
                if self.announce != message.payload:
                    client.publish(self.automatedHomeTopic + "/announce", message.payload)
                    self.announce = message.payload

        except Exception as e:
            logging.error("EXCEPTION RAISED: " + str(e))
            

    def loop_and_run(self, wait=15):
        '''
        This routine runs a loop and checks whether a message is received from the broker.

        Args:
            wait (int):  timeout

        Returns:
            None

        Raises:
            Exception: Receiving message

        '''

        while True:
            try:
                self.clientBroker.loop(wait)
                time.sleep(1)
                
            except Exception as e:
                logging.error("EXCEPTION RAISED: " + str(e))


if __name__ == "__main__":
    # check arguments
    if len(sys.argv) != 2:
        print(f"Use: python Shelly.py <config file>")
        exit(0)

    # This will prepare the logs
    logging.basicConfig(filename=sys.argv[1] + '.' + date.today().isoformat() + _FILE_LOG_SUFFIX_, filemode='a', format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("\n\n***** ***** ***** *****")

    # Configuration of the shelly device
    params_shelly = config(sys.argv[1], "shelly")
    params_broker = config(sys.argv[1], "broker")
    logging.info(params_shelly)
    logging.info(params_broker)
    shelly = Shelly(params_shelly['topic'], params_shelly['room'], params_shelly['device'], params_broker['ip'], int(params_broker['port']))

    logging.info("This is the programe acting as Shelly Device\n")
    logging.info("Virtual Device Service is RUNNING")

    # it stays indefinitely in updating status
    shelly.loop_and_run()
