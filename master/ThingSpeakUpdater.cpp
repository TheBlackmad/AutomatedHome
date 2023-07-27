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
*
* Name: ThingSpeakUpdater.cpp
*
* Author: TheBlackmad
*
* Description:
* Translation of Mosquitto Topics to Thingspeak Topics
*
*******************************/
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "ThingSpeakUpdater.hpp"
#include "autohome.hpp"

ThingSpeakUpdater::ThingSpeakUpdater(AutomatedHome *h) {
    /*
        Constructor

        Args:
            AutomatedHome *h: AutomateHome object

        Returns:
            a ThingSpeakUpdater Object

        Raises:
            None
    */

	this->h = h;
}

ThingSpeakUpdater::~ThingSpeakUpdater() {
    /*
        Destructor

        Args:
            None

        Returns:
            None

        Raises:
            None
    */
}
	
int ThingSpeakUpdater::update() {
    /*
        This method copies the values of the devices in the rooms in a special topic that is link to the 
        ThingSpeak MQTT Server (MatLab). This new Mosquitto MQTT Topic is configured in the MQTT Server
	so regularly is updating the ThingSpeak Servers with its data. 

        Args:
            void

        Returns:
            None

        Raises:
            None
    */

    char ts_topic[256], ts_value[256];
/*    room *pRoom;
    vector<room> rooms;
    vector<iotdevice*> devices;
*/   
    vector<string> rooms;
    string oneroom;

    // update to ThingSpeak
/*    while (1) {
		fprintf (stdout, "(thingSpeakUpdater::update) Running the update\n");
		// for each room
		rooms = this->h->getRooms();
        for (vector<room>::iterator it=rooms.begin(); it!=rooms.end(); ++it) {
            pRoom = &(*it);
            if ( _TS_DEBUG_ ) fprintf (stdout, "(thingSpeakUpdater::update) Going to send to ThingSpeak Room %s\n", pRoom->getName().c_str());
			this->translate_feed (pRoom, ts_topic, ts_value);
                
			if (_TS_DEBUG_) fprintf (stdout, "(thingSpeakUpdater::update) Topic: %s\tValue: %s\n", ts_topic, ts_value);
			mosquitto_publish(this->h->mosq, NULL, ts_topic, strlen(ts_value), ts_value, 0, 0);

			sleep(_TS_UPDATE_LIMIT_); // update Thingspeak with delay (free account)
            
        } // for rooms
        
        sleep(_TS_UPDATE_RATE_); // frequency for theupdate
        
    }*/
    while (1) {
		fprintf (stdout, "(thingSpeakUpdater::update) Running the update\n");
		// for each entry in the MQTT
		rooms = this->h->getVectorRoom();
        for (vector<string>::iterator it=rooms.begin(); it!=rooms.end(); ++it) {
            oneroom = (*it);
            if ( _TS_DEBUG_ ) fprintf (stdout, "(thingSpeakUpdater::update) Going to send to ThingSpeak Room %s\n", oneroom.c_str());
			this->translate_feed ((char*)oneroom.c_str(), ts_topic, ts_value);
                
			if (_TS_DEBUG_) fprintf (stdout, "(thingSpeakUpdater::update) Topic: %s\tValue: %s\n", ts_topic, ts_value);
			mosquitto_publish(this->h->mosq, NULL, ts_topic, strlen(ts_value), ts_value, 0, 0);

			sleep(_TS_UPDATE_LIMIT_); // update Thingspeak with delay (free account)
            
        } // for rooms
		
		fprintf (stdout, "(thingSpeakUpdater::update) Update finished\n");
        
        sleep(_TS_UPDATE_RATE_); // frequency for theupdate
        
    }	
}

//int ThingSpeakUpdater::translate_feed (room* raum, char* ts_topic, char* ts_value) {
int ThingSpeakUpdater::translate_feed (char* raum, char* ts_topic, char* ts_value) {
    /*
        This method translates topics from Mosquitto MQTT Brooker to those in the ThingSpeak Servers

        Args:
            char* raum: room dedicated
	    char* ts_topic: thinkspeak topic (output)
	    char* ts_value: thingspeak value (output)

        Returns:
            None

        Raises:
            None
    */

	char r[256], k[32], str[256]="\0";

	
	// check args
	if ( (raum==NULL) || (ts_topic==NULL) || (ts_value==NULL) )
		return -1;
		
	if (_TS_DEBUG_) fprintf (stdout, "(ts_translate_feed) Room: %s\n", raum);
		
	// get Room. 
//	if ( this->getRoom((char*)raum->getName().c_str(), r) != 0 ) {
	if ( this->getRoom(raum, r) != 0 ) {
		return -1;
	}
	if (_TS_DEBUG_) fprintf (stdout, "(ts_translate_feed) Room: %s\n", r);
	
	// get Key
//	if ( this->getKey((char*)raum->getName().c_str(), k) != 0 ) {
	if ( this->getKey(raum, k) != 0 ) {
		return -1;
	}
	if (_TS_DEBUG_) fprintf (stdout, "(ts_translate_feed) Key: %s\n", k);

	// get Value
	if ( this->getValueFeed(raum, ts_value) != 0 ) {
		return -1;
	}
	
	// prepare string for Thingspeak
	// in the form like "1095393/publish/MBL7XUE46B3OC1AS" Values "field1=18.500000&field2=62.700001&field3=2.960000&field4=-82"
	strcat (&str[0], r);
	strcat (&str[0], "/publish/");
	strcat (&str[0], k);	
	strcpy (ts_topic, &str[0]);
	
	if (_TS_DEBUG_) fprintf (stdout, "Topic: %s\tValue: %s\n", ts_topic, ts_value);
	
	return 0;
	
}

int ThingSpeakUpdater::getRoom (char* raum, char* ts_raum) {
    /*
        This method gives the Thingspeak room value for a given room

        Args:
            char* raum: room 
            char* ts_raum: thinkspeak room (output)

        Returns:
            None

        Raises:
            None
    */

	// check args
	if ( (raum == NULL) || (ts_raum == NULL) ) {
		return -1;
	}
	
	if (_TS_DEBUG_) fprintf (stdout, "(ts_getRoom) Room: %s\n", raum);

	if ( strcmp(raum, "room0R") == 0 ) {
		strcpy (ts_raum, _TS_CHANNEL_0R_);
	}
	else if ( strcmp(raum, "room0L") == 0 ) {
		strcpy (ts_raum, _TS_CHANNEL_0L_);		
	}
	else if ( strcmp(raum, "room1R") == 0 ) {
		strcpy (ts_raum, _TS_CHANNEL_1R_);
	}
	else if ( strcmp(raum, "room1L") == 0 ) {
		strcpy (ts_raum, _TS_CHANNEL_1L_);
	}
	else if ( strcmp(raum, "room2R") == 0 ) {
		strcpy (ts_raum, _TS_CHANNEL_2R_);
	}
	else if ( strcmp(raum, "room2L") == 0 ) {
		strcpy (ts_raum, _TS_CHANNEL_0L_);
	}
	else if ( strcmp(raum, "room3R") == 0 ) {
		strcpy (ts_raum, _TS_CHANNEL_3R_);
	}
	else if ( strcmp(raum, "room3L") == 0 ) {
		strcpy (ts_raum, _TS_CHANNEL_3L_);
	}
	else {
		return -1;
	}
	
	return 0;
	 
}

int ThingSpeakUpdater::getKey (char* raum, char* key) {
    /*
        This method gets the ThingSpeak key value for a room

        Args:
            char* raum: room 
            char* key: ThingSpeak key for the room (output)

        Returns:
            None

        Raises:
            None
    */

	// check args
	if ( (raum == NULL) || (key == NULL) ) {
		return -1;
	}

	if (_TS_DEBUG_) fprintf (stdout, "(ts_getKey) Room: %s\n", raum);
	
	if ( strcmp(raum, "room0R") == 0 ) {
		strcpy (key, _TS_WRITE_API_KEY_0R_);
	}
	else if ( strcmp(raum, "room0L") == 0 ) {
		strcpy (key, _TS_WRITE_API_KEY_0L_);		
	}
	else if ( strcmp(raum, "room1R") == 0 ) {
		strcpy (key, _TS_WRITE_API_KEY_1R_);
	}
	else if ( strcmp(raum, "room1L") == 0 ) {
		strcpy (key, _TS_WRITE_API_KEY_1L_);
	}
	else if ( strcmp(raum, "room2R") == 0 ) {
		strcpy (key, _TS_WRITE_API_KEY_2R_);
	}
	else if ( strcmp(raum, "room2L") == 0 ) {
		strcpy (key, _TS_WRITE_API_KEY_2L_);
	}
	else if ( strcmp(raum, "room3R") == 0 ) {
		strcpy (key, _TS_WRITE_API_KEY_3R_);
	}
	else if ( strcmp(raum, "room3L") == 0 ) {
		strcpy (key, _TS_WRITE_API_KEY_3L_);
	}
	else {
		return -1;
	}
	
	return 0;
	 
}

int ThingSpeakUpdater::getValueFeed (char* raum, char* ts_value) {
    /*
        This method gets the ThingSpeak values for a defined room

        Args:
            char* raum: room 
            char* key: ThingSpeak values for the room (output)

        Returns:
            None

        Raises:
            None
    */

/*	iotdevice* dev;
	DHT22 *ptr;
	vector<iotdevice*> devices;
	char value[64];*/

	vector<Topic*> topics;
	string s, att;
	
	// check args
	if ( (raum == NULL) || (ts_value == NULL) ) {
		return -1;
	}
	
	// iterate on rooms
/*	devices = raum->getDevices();
	for (vector<iotdevice*>::iterator it=devices.begin(); it!=devices.end(); ++it) {
		dev = (*it);
		// if the device is DHT22
		if ( dev->getId() == _DHT22_ID_ ) {
			ptr = (DHT22*) dev;
			// prepare the values
			strcpy (ts_value, "\0");
			// field temperature
			strcat (ts_value, _TS_FIELD_TEMPERATURE_);
			strcat (ts_value, "=");
			sprintf (value,"%f", ptr->getTemperature());
			strcat (ts_value, value);
			strcat (ts_value, "&");
			// field humidity
			strcat (ts_value, _TS_FIELD_HUMIDITY_);
			strcat (ts_value, "=");
			sprintf (value,"%f", ptr->getHumidity());
			strcat (ts_value, value);
			strcat (ts_value, "&");
			// field battery
			strcat (ts_value, _TS_FIELD_BATTERY_);
			strcat (ts_value, "=");
			sprintf (value,"%f", ptr->getBattery());
			strcat (ts_value, value);
			strcat (ts_value, "&");
			// field rssi
			strcat (ts_value, _TS_FIELD_RSSI_);
			strcat (ts_value, "=");
			sprintf (value,"%d", ptr->getRSSI());
			strcat (ts_value, value);
			
			return 0;
		}
	}
*/		
	topics = this->h->getVectorTopics();
	s = string ("/") + string(raum) + string("/") + string ("DHT22") + string ("/");

	// prepare the values
	strcpy (ts_value, "\0");

	for (vector<Topic*>::iterator it=topics.begin(); it!=topics.end(); ++it) {
		
		if ( (*it)->getName().find(s) == 0 ) {
			
			// get the attribute temperature, humidity...
			att = (*it)->getName().substr ( s.length() );
			
			if ( att.compare("temperature") == 0 ) {
				// field temperature
				strcat (ts_value, _TS_FIELD_TEMPERATURE_);
				strcat (ts_value, "=");
				strcat (ts_value, (*it)->getValue().c_str());
				strcat (ts_value, "&");
			}
			else if ( att.compare("humidity") == 0 ) {
				// field temperature
				strcat (ts_value, _TS_FIELD_HUMIDITY_);
				strcat (ts_value, "=");
				strcat (ts_value, (*it)->getValue().c_str());
				strcat (ts_value, "&");				
			}
			else if ( att.compare("battery") == 0 ) {
				// field temperature
				strcat (ts_value, _TS_FIELD_BATTERY_);
				strcat (ts_value, "=");
				strcat (ts_value, (*it)->getValue().c_str());
				strcat (ts_value, "&");				
			}
			else if ( att.compare("rssi") == 0 ) {
				// field temperature
				strcat (ts_value, _TS_FIELD_RSSI_);
				strcat (ts_value, "=");
				strcat (ts_value, (*it)->getValue().c_str());
			}
		}
		
	}
	
	return 0;
	
}

