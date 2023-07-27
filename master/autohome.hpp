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

#ifndef __AUTOMATEDHOME__
#define __AUTOMATEDHOME__

#include <iostream>
#include <string>
#include <vector>
#include <iterator>
#include <time.h>
#include "ThingSpeakUpdater.hpp"
#include "TelegramInterface.hpp"

#define _AH_MAX_STRING_			80
#define _AH_TOPIC_INDEX_		0
#define _AH_VALUE_INDEX_		30
#define _AH_DATE_INDEX_			50


using namespace std;

class ThingSpeakUpdater;
class TelegramInterface;

//
/* Class Topic
 * 
 * This class represents the Topics List in the Automated Home
 * 
 */
class Topic {
	
	private:
	string name;		// topic name
	string value;		// topic value
	time_t created;		// time when created
	time_t lastUpdate;	// last Update of the topic
	long int nUpdates;	// number of updates
	
	
	public:
	Topic(string name, string value);
	~Topic();
	string getName(void);
	string getValue(void);
	void setValue(string v);
	string createdOn(void);
	string lastUpdateOn(void);
	long int getnUpdates(void);
	string printTopic(void);
	string printTopicName(void);
	string printStatus(void);
		
};

//
/* Class AutomatedHome
 * 
 * This class represents the AutomatedHome
 * 
 */

class AutomatedHome {

	private:
	string name;
	time_t created;		// time when created
	vector<Topic*> topics;
	TelegramInterface *tiController;  // Controller for the TelegramServer 
	ThingSpeakUpdater *tsUpdater;  // Updater to ThingSpeak Broker, through the Mosquitto Broker

	int contained(string r, vector<string> rooms);
	
	
	public:
	struct mosquitto *mosq;
	AutomatedHome(string name, struct mosquitto *mosq);
	~AutomatedHome();
	string getName(void);
	string createdOn(void);
	int registerMessage(string topic, string value);
	string printTopics(void);
	string getTopics(void);
	string printStatus(void);
	vector<Topic*> getVectorTopics (void);
	vector<string> getVectorRoom (void);

	void tsUpdate(void); // update to ThingSpeak 
	void tiServer(void);

};

#endif
