/* TheBlackmad
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
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <mosquitto.h>
#include "autohome.hpp"


#define _ID_                        "Client_C"
#define _BROKER_                    "127.0.0.1"
#define _PORT_                      1883
#define _TOPIC1_                    "/Room0R/#"
#define _TOPIC2_                    "/Room0L/#"
#define _TOPIC3_                    "/Room1R/#"
#define _TOPIC4_                    "/Room1L/#"
#define _TOPIC5_                    "/Room2R/#"
#define _TOPIC6_                    "/Room2L/#"
#define _TOPIC7_                    "/Room3R/#"
#define _TOPIC8_                    "/Room3L/#"
#define _TOPIC_TS_                  "1096861/publish/fields/field1/M5BCT5XQFE93V9HT"
// MQTT Topic for controlling the master
#define _TOPIC_MASTER_              "#"
#define _TOPIC_ROOT_1_              "/room"
#define _TOPIC_ROOT_2_              "/garden"
#define _TOPIC_ROOT_3_              "/entrance"

#define _LOGFILE_                   "ah_master.log"
#define _LOG_TO_FILE_               1

AutomatedHome* h;

void* thingSpeakUpdate (void* vargp);
void* telegramServer (void* vargp);
void tgHelp (char out[], char in[]);
void tgList (char out[], char in[]);
void tgStatus (char out[], char in[]);

void on_message (struct mosquitto *mosq, void *userdata, const struct mosquitto_message *msg)
    /*
        This routine is the callback function for the MQTT Broker connections

        Args:
            struct mosquitto *mosq: Connection to the broker
            void *userdata: area for user data for the callback
            const struct mosquitto_message *msg: MQTT message received

        Returns:
            void

        Raises:
            None
    */
{
    // If the topic starts with /room this is then a new status
    if ( 
        (strncmp (msg->topic, _TOPIC_ROOT_1_, strlen(_TOPIC_ROOT_1_)) == 0) ||
        (strncmp (msg->topic, _TOPIC_ROOT_2_, strlen(_TOPIC_ROOT_2_)) == 0) ||
        (strncmp (msg->topic, _TOPIC_ROOT_3_, strlen(_TOPIC_ROOT_3_)) == 0)
        ) {
        h->registerMessage(string ((char*)msg->topic), string((char*)msg->payload));
//	cout << "Received:"<<endl;
//	cout << "    ---> " << (char*)msg->topic << " : " << (char*)msg->payload << endl;
    }

}


int main(int argc, char *argv[])
{
    struct mosquitto *mosq;
    char data[128];
    pthread_t thread_id1, thread_id2;
    
    // Redirect output to logfile?
    if ( _LOG_TO_FILE_ )
        freopen(_LOGFILE_, "w", stdout);
    
    // Create a connection to the MQTT Server and set the callback
    if ( !(mosq = mosquitto_new(_ID_, false, data)) ) {
        fprintf (stdout, "Error creating instance of mosquitto\n");
        return -1;
    }
    mosquitto_message_callback_set(mosq, on_message);
    cout << "Connecting to mosquitto broker" << endl;
    if ( mosquitto_connect(mosq, _BROKER_, _PORT_, 60) !=  MOSQ_ERR_SUCCESS ) {
        fprintf (stdout, "Error connecting to broker\n");
        return -1;
    }

    // create a new object AutomatedHome linked to the MQTT Server.
    h = new AutomatedHome("My SVT", mosq);
    cout << "TOPICS:\n" + h->printTopics();

    // subcribe to the TOPIC MASTER. Subcription to an IoT device is automatically
    // once the device register itself in the MQTT through the topic master.
   if ( mosquitto_subscribe(mosq, NULL, _TOPIC_MASTER_, 0) != MOSQ_ERR_SUCCESS ) {
        fprintf (stdout, "Error subscribing to %s\n", _TOPIC_MASTER_ );
        return -1;
    }

    // create the thread that will update to ThingSpeak and Telegram
    cout << "Creating thread for ThingSpeakUpdate" << endl;
    if ( pthread_create (&thread_id1, NULL, thingSpeakUpdate, NULL) != 0 ) {
        cout << "Error creating the pthread ThingSpeakUpdate" << endl;
        return -1;
    }

    cout << "Creating thread for TelegramServer" << endl;
    if ( pthread_create (&thread_id2, NULL, telegramServer, NULL) != 0 ) {
        cout << "Error creating the pthread TelegramServer" << endl;
        return -1;
    }

    while (1) {
        mosquitto_loop(mosq, -1, 1);  // this calls mosquitto_loop() in a loop, it will exit once the client disconnects cleanly
        fflush(stdout);
    }

    return 0;
}

void* telegramServer (void* vargp) {
    /*
        This routine creates a telegram server to connect to  and get information
        through telegram channel

        Args:
            void* vargp: args for the thread

        Returns:
            NULL

        Raises:
           None
    */
    // this is running in an eternal loop for the Telegram Server
    cout << "(Thread::telegramServer) Thread for TelegramServer started" << endl; 
    sleep(2);
    h->tiServer();
    
    return NULL;
    
}

void* thingSpeakUpdate (void* vargp) {
    /*
        This routine creates an update to the ThingSpeak account

        Args:
            void* vargp: args for the thread
        Returns:
            NULL

        Raises:
            None
    */
    // this is running in an eternal loop updating as needed the ThingSpeak Broker
    cout << "(Thread::thingSpeakUpdate) Thread for updating the ThingSpeak started" << endl; 
    sleep(2);
    h->tsUpdate();
    
    return NULL;
    
}
