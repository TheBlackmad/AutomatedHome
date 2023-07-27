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

#include <iostream>
#include <string>
#include <cstring>
#include <vector>
#include "autohome.hpp"

using namespace std;

/*
 * *******************************
 * SECTION FOR TOPIC
 * *******************************
 */
 
/*
 * Contructor
 * 
 * Input:
 * 		name: name of the Topic
 * 
 * Output:
 * 		Object Topic
 */
Topic::Topic(string name, string value) {
	this->name = name;
	this->value = value;
	time ( &(this->created) );
	time ( &(this->lastUpdate) );
}

/*
 * Destructor
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		none
 */
Topic::~Topic() {}

string Topic::getName(void) {
	return this->name;
}

/*
 * getValue
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		value
 */
string Topic::getValue(void) {
	return this->value;
}

/*
 * setValue
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		value
 */
void Topic::setValue(string v) {
	time_t rawtime;
	
	this->value = v;
	this->lastUpdate = time (&rawtime);

	return;
}

/*
 * createdOn
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - when topic was created
 */
string Topic::createdOn(void) {

	string s;
	struct tm *timeinfo;
	time_t rawtime;
	
	rawtime = this->created;
	timeinfo = localtime( &rawtime );
	s = string (asctime(timeinfo));
	
	return s;
}

/*
 * lastUpdate
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - when topic was last updated
 */
string Topic::lastUpdateOn(void) {
	string s;
	struct tm *timeinfo;
	time_t rawtime;
	
	rawtime = this->lastUpdate;
	timeinfo = localtime( &rawtime );
	s = string (asctime(timeinfo));
	
	return s;
}

/*
 * getnUpdates
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		long int - returns the number of updates since creation
 */
long int Topic::getnUpdates(void) {
	return this->nUpdates;
}

/*
 * printTopic
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - returns topic and value and date
 */
string Topic::printTopic(void) {
	char buffer[_AH_MAX_STRING_];
	
	// init buffer
	memset(buffer, ' ', _AH_MAX_STRING_);
	buffer[_AH_MAX_STRING_ - 1] = '\000';
	
	strcpy(buffer+_AH_TOPIC_INDEX_, this->getName().c_str()); buffer[strlen(this->getName().c_str())] = ' ';
	strcpy(buffer+_AH_VALUE_INDEX_, this->getValue().c_str()); buffer[_AH_VALUE_INDEX_+strlen(this->getValue().c_str())] = ' ';
	strcpy(buffer+_AH_DATE_INDEX_, this->lastUpdateOn().c_str());	
	
	return string(buffer);
//	return /*"Created on " + this->createdOn() +*/ this->getName() + "\t" + this->getValue() + "\t" + this->lastUpdateOn();
}

/*
 * printTopicName
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - returns topic and value and date
 */
string Topic::printTopicName(void) {
	char buffer[_AH_MAX_STRING_];
	
	// init buffer
	memset(buffer, ' ', _AH_MAX_STRING_);
	buffer[_AH_MAX_STRING_ - 1] = '\000';
	
	strcpy(buffer+_AH_TOPIC_INDEX_, this->getName().c_str()); buffer[strlen(this->getName().c_str())] = '\n';
	
	return string(buffer);
//	return /*"Created on " + this->createdOn() +*/ this->getName() + "\t" + this->getValue() + "\t" + this->lastUpdateOn();
}

/*
 * printStatus
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - returns topic and value
 */
string Topic::printStatus(void) {
	char buffer[_AH_MAX_STRING_];
	
	// init buffer
	memset(buffer, ' ', _AH_MAX_STRING_);
	buffer[_AH_MAX_STRING_ - 1] = '\000';
	
	strcpy(buffer+_AH_TOPIC_INDEX_, this->getName().c_str()); buffer[strlen(this->getName().c_str())] = ' ';
	strcpy(buffer+_AH_VALUE_INDEX_, this->getValue().c_str()); buffer[_AH_VALUE_INDEX_+strlen(this->getValue().c_str())] = '\n';
	buffer[_AH_VALUE_INDEX_+strlen(this->getValue().c_str())+1] = '\000';
	
	return string(buffer);
//	return /*"Created on " + this->createdOn() +*/ this->getName() + "\t" + this->getValue() + "\t" + this->lastUpdateOn();
}




/*
 * *******************************
 * SECTION FOR AUTOMATEDHOME
 * *******************************
 */

/*
 * Contructor
 * 
 * Input:
 * 		name: name of the AutomatedHome
 * 
 * Output:
 * 		Object AutomatedHome
 */ 
AutomatedHome::AutomatedHome(string name, struct mosquitto* mosq) {
	this->name = name;
	this->mosq = mosq;
	time ( &(this->created) );
	this->tiController = new TelegramInterface(this);
	this->tsUpdater = new ThingSpeakUpdater(this);


}

/*
 * Destructor
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		none
 */
AutomatedHome::~AutomatedHome() {}

/*
 * getName
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		name
 */
string AutomatedHome::getName(void) {
	return this->name;
}

/*
 * createdOn
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - when automatedhome was created
 */
string AutomatedHome::createdOn(void) {

	string s;
	struct tm *timeinfo;
	time_t rawtime;
	
	rawtime = this->created;
	timeinfo = localtime( &rawtime );
	s = string (asctime(timeinfo));
	
	return s;

}

/*
 * registerMessage
 * It registers a message topic with its value. If it is a new topic, it inserts for the first time
 * otherwise its value is updated.
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		0 - Ok
 * 		-1 - Error
 */
int AutomatedHome::registerMessage(string newTopic, string value) {

	vector<Topic*>::iterator it; 
	Topic* ptr;
	Topic *t;
	
	// if newTopic ALREADY registered, update the value
	for (it=this->topics.begin(); it!=this->topics.end(); ++it) {
		
		ptr = *it;
		if ( ptr->getName().compare(newTopic) == 0 ) {

			// update the value
			ptr->setValue(value);			
			
			return 0;
		}
	
	}
	
	// if newTopic NOT registered, create the new topic and include in the list.
	t = new Topic (newTopic, value);
	it = this->topics.end();
	this->topics.insert(it, t);
	
	return 0;
}


/*
 * printTopics
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - returns a string with all topics and values
 */
string AutomatedHome::printTopics(void) {
	
	vector<Topic*>::iterator it; 
	Topic* ptr;
	string s;

	// Print out content of AutomatedHome
	s = "" + this->getName() + " Created on " + this->createdOn();
	
	// if newTopic ALREADY registered, update the value
	for (it=this->topics.begin(); it!=this->topics.end(); ++it) {
		
		ptr = *it;
		
		s = s + ptr->printTopic();
		
	}
	
	return s;
	
}

/*
 * printTopics
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - returns a string with all topics and values
 */
string AutomatedHome::getTopics(void) {
	
	vector<Topic*>::iterator it; 
	Topic* ptr;
	string s;

	
	// if newTopic ALREADY registered, update the value
	for (it=this->topics.begin(); it!=this->topics.end(); ++it) {
		
		ptr = *it;
		
		s = s + ptr->printTopicName();
		
	}
	
	return s;
	
}

/*
 * printStatus
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		string - returns a string with all topics and values
 */
string AutomatedHome::printStatus(void) {
	
	vector<Topic*>::iterator it; 
	Topic* ptr;
	string s;

	// Print out content of AutomatedHome
	s = "" + this->getName() + " Created on " + this->createdOn();
	
	// if newTopic ALREADY registered, update the value
	for (it=this->topics.begin(); it!=this->topics.end(); ++it) {
		
		ptr = *it;
		
		s = s + ptr->printStatus();
		
	}
	
	return s;
	
}

/*
 * getVectorTopics
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		vector<Topic*> - copy of vector of topics
 */
vector<Topic*> AutomatedHome::getVectorTopics (void) {
	return this->topics;
}

/*
 * getVectorRoom
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		vector<string> - vector os strings with room names
 */
vector<string> AutomatedHome::getVectorRoom (void) {
	
	vector<string> rooms;
	string r;
	Topic *t;
	int pos;

	// Get all rooms for all topics
	for (vector<Topic*>::iterator it=this->topics.begin(); it!=this->topics.end(); ++it) {
	
		// find rooms and include them in the new vector
		t = (*it);
		pos = t->getName().find("/", 1);
		r = t->getName().substr(1, pos-1);
		
		// if not contained in the rooms vector, then include it
		if ( this->contained (r, rooms) == 0 )
			rooms.push_back (r);

	}

	return rooms;
	
}

/*
 * contained
 * check whether string is included in a vector
 * 
 * Input:
 * 		none
 * 
 * Output:
 * 		0 - string r is not in rooms
 * 		1 - string r is in rooms
 */
int AutomatedHome::contained(string r, vector<string> rooms) {

	for ( vector<string>::iterator it=rooms.begin(); it!=rooms.end(); ++it ) {

		// string r is found in rooms ?
		if ( (*it).compare(r) == 0 ) {
			return 1;
		}
		
	}
	
	return 0;

}



/*
 * tiServer
 * 		Launch the TelegramServer for bots
 * 
 * Input:
 *		none
 * 
 * Output:
 * 		void
 */
void AutomatedHome::tiServer(void) {
	this->tiController->telegramServer();
}

/*
 * tsUpdate
 * 		Performs update into ThingSpeak
 * 
 * Input:
 *		none
 * 
 * Output:
 * 		void
 */
void AutomatedHome::tsUpdate(void) {
	this->tsUpdater->update();
}
