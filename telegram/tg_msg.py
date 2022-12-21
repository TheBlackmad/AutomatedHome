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

import sys
import paho.mqtt.client as mqtt #import the client1
from time import sleep      # Importing the time library to provide the delays in program,
import datetime

# importing all required libraries
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events, utils

import logging

def tg_send_message (tg_id, tg_message):
    '''
        This routine sends a message to a given user

        Args:
            tg_id (str): Id of the user to send the message to
            tg_message (str): message to send

        Returns:
            None

        Raises:
            Exception: Section not found in the file
            Exception: Error in reading file
    '''

    print ("Sending to ", tg_id, "Message: " + tg_message)

    try:
        # sending message using telegram client
        client_tg.send_message(utils.get_input_peer(client_tg.get_entity(tg_id)), tg_message, parse_mode='html')

    except Exception as e:
        raise(f"Error sending message: {str(e)}")

def on_message(client, userdata, message):
    '''
        This routine is called when received a telegram message

        Args:
            client: client object
            userdata: data referencing the originator
            message (str): message received

        Returns:
            None

        Raises:
            Exception: Receiving message

    '''
    global tg_id_x
    global tg_msg_x

    try:
        payload = str(message.payload.decode("utf-8"))
        print("message received " , payload)
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)
        
        # Here get the user_id to whom to send it and the message
        tg_id_x = int(payload[0:payload.find(' ')])
        tg_msg_x = payload[payload.find(' ')+1:]

    except Exception as e:
        print (f"(Main OnMessage - {str(datetime.datetime.now())} EXCEPTION RAISED: {str(e)}")

########################################
##
## ALL MQTT CONFIGURATION
##

# get your api_id, api_hash, token
# from telegram as described above
api_id = '<YOUR-API-ID>'
api_hash = '<YOUR-API-HASH>'
token = '<YOUR-TELEGRAM-TOKEN>'
broker_address = "192.168.178.10" #"127.0.0.1"
topic_message = "/tg_msg/message"

logtofile = 1   #if log to file = 1; otherwise to stdout = 0
filetolog = "tg_sender.log"

tg_id_x = 0
tg_msg_x = ""

if __name__ == "__main__":

    # Preparing the logging
    logging.basicConfig(format="%(asctime)s - %(funcName)s:%(lineno)d - %(message)s", level=logging.INFO)
    logging.info("Telegram Listener for Automated Home version 0.1")

    # Redirecting stdout to a file.
    if logtofile:
        sys.stdout = open(filetolog, "w")

    try:

        #broker_address="iot.eclipse.org"1
        logging.info("(TG_MSG) Creating new instance of MQTT Broker")
        client = mqtt.Client("P1") #create new instance

        logging.info("(TG_MSG) Connecting to broker")
        client.connect(broker_address) #connect to broker

        client.loop_start() #start the loop

        logging.info("Subscribing to topic: " + topic_message)
        client.subscribe(topic_message)

        client.on_message=on_message        #attach function to callback

        # creating a telegram session and assigning
        # it to a variable client_tg
        client_tg = TelegramClient('session', api_id, api_hash)

        # connecting and building the session
        client_tg.connect()
        client_tg.start(bot_token=token)

    except Exception as e:
        logging.error (f"(Main Config -  {str(datetime.datetime.now())} EXCEPTION RAISED: {str(e)}")

    while True:

        try:
            if tg_id_x != 0:
                tg_send_message (tg_id_x, tg_msg_x)
                tg_id_x = 0
                tg_id_msg = ""

            sleep(0.5)

            sys.stdout.flush()

        except Exception as e:
            logging.error (f"(Main Loop - {str(datetime.datetime.now())} EXCEPTION RAISED: str(e)")


    # disconnecting the telegram session and broker
    client.disconnect()
    client_tg.disconnect()

