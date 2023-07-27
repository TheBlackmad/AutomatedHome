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
* Name: ThingSpeakUpdater.hpp
*
* Author: TheBlackmad
*
* Description:
* Translation of Mosquitto Topics to Thingspeak Topics
*
*******************************/

#ifndef __THINGSPEAK__
#define __THINGSPEAK__

#include <iostream>
#include <string>
#include <mosquitto.h>
#include "autohome.hpp"

// Flags for debug mode: 1 active; 0 inactive
#define _TS_DEBUG_				1

// Replace with your ThinSpeak credentials
#define _TS_SERVER_			"mqtt.thingspeak.com"
#define _TS_SERVERPORT_			1883
#define _TS_MQTT_USERNAME_		"<your username>"
#define _TS_MQTT_PASSWORD_		"<your password>"
#define _TS_USER_API_KEY_		"<your api key>"
// ThinkSpeak Channels
#define _TS_CHANNEL_0R_			"<your channel"
#define _TS_CHANNEL_0L_			""
#define _TS_CHANNEL_1R_			""
#define _TS_CHANNEL_1L_			"<your channel>"
#define _TS_CHANNEL_2R_			"<your channel>"
#define _TS_CHANNEL_2L_			""
#define _TS_CHANNEL_3R_			""
#define _TS_CHANNEL_3L_			"<your channel>"
// ThinkSpeak Write API Keys
#define _TS_WRITE_API_KEY_0R_	"<your write key>"
#define _TS_WRITE_API_KEY_0L_	""
#define _TS_WRITE_API_KEY_1R_	""
#define _TS_WRITE_API_KEY_1L_	"<your write key>"
#define _TS_WRITE_API_KEY_2R_	"<your write key>"
#define _TS_WRITE_API_KEY_2L_	""
#define _TS_WRITE_API_KEY_3R_	""
#define _TS_WRITE_API_KEY_3L_	"<your write key>"
// ThinkSpeak Read API Keys
#define _TS_READ_API_KEY_0R_	"<your read key>"
#define _TS_READ_API_KEY_0L_	""
#define _TS_READ_API_KEY_1R_	""
#define _TS_READ_API_KEY_1L_	"<your read key>"
#define _TS_READ_API_KEY_2R_	"<your read key>"
#define _TS_READ_API_KEY_2L_	""
#define _TS_READ_API_KEY_3R_	""
#define _TS_READ_API_KEY_3L_	"<your read key>"
// Thinkspeak Fields for each channel
#define _TS_FIELD_TEMPERATURE_	"field1"
#define _TS_FIELD_HUMIDITY_		"field2"
#define _TS_FIELD_BATTERY_		"field3"
#define _TS_FIELD_RSSI_			"field4"
#define _TS_FIELD_LIGHTS_		"field5"
// Update rate in seconds (free account?)
#define _TS_UPDATE_RATE_    	900		// update frequency ofdata 900=15mins
#define _TS_UPDATE_LIMIT_		20		// one request every 20 seconds       

class AutomatedHome;

class ThingSpeakUpdater {

	private:
	AutomatedHome *h;

	public:
	// methods
	ThingSpeakUpdater(AutomatedHome *h);
	~ThingSpeakUpdater();
	
	int update (void);
	int translate_feed (char* raum, char* ts_topic, char* ts_value);
	int getValueFeed (char* raum, char* ts_value);

	private:
	int getRoom (char* raum, char* ts_raum);
	int getKey (char* raum, char* key);

};
 
#endif

