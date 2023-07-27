/******************************
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
*
* Name: TelegramInterface.cpp
*
* Author: TheBlackmad
*
* Description:
* Interface to Telegram bots
*
*******************************/
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <mosquitto.h>
#include "TelegramInterface.hpp"
#include "autohome.hpp"

TelegramInterface::TelegramInterface(AutomatedHome *h) {
    /*
        Constructor

        Args:
            AutomatedHome *h: AutomateHome object

        Returns:
            a Telegram Interface Object

        Raises:
            None
    */
    this->h = h;
}

TelegramInterface::~TelegramInterface() {
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

void TelegramInterface::telegramServer(void) {
    /*
        This method create a Telegram Interface Server connection where clients connect and send their messages.
        The function of this server is to connect to a  program that receives messages Telegram. That program sends
        messages to this server, who populates a Topic specific for a device in the MQTT the request.

        Each device is listening on the topic in the MQTT Server to receive orders and each device controller is
        responsible to act accordingly.

        Args:
            void

        Returns:
            None

        Raises:
            None
    */

    int listenfd = 0, connfd = 0, n=0;
    struct sockaddr_in serv_addr;
    char sendBuff[8192], recvBuff[8192], value[32];
//    time_t ticks;

    /* creates an UN-named socket inside the kernel and returns
     * an integer known as socket descriptor
     * This function takes domain/family as its first argument.
     * For Internet family of IPv4 addresses we use AF_INET
     */
    listenfd = socket(AF_INET, SOCK_STREAM, 0);
    memset(&serv_addr, '0', sizeof(serv_addr));
    memset(sendBuff, '0', sizeof(sendBuff));
    memset(recvBuff, '0', sizeof(recvBuff));

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(_TI_PORT_);

    /* The call to the function "bind()" assigns the details specified
     * in the structure 『serv_addr' to the socket created in the step above
     */
    fprintf (stdout, "(telegramServer) Creating socket for telegram . . .\n");  
    bind(listenfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr));

    /* The call to the function "listen()" with second argument as 10 specifies
     * maximum number of client connections that server will queue for this listening
     * socket.
     */
    fprintf (stdout, "(telegramServer) Listening for connections . . .\n");  
    listen(listenfd, 10);

    while(1)
    {
	/* In the call to accept(), the server is put to sleep and when for an incoming
	 * client request, the three way TCP handshake* is complete, the function accept()
	 * wakes up and returns the socket descriptor representing the client socket.
	 */
	connfd = accept(listenfd, (struct sockaddr*)NULL, NULL);
	fprintf (stdout, "(telegramServer) Here we have a Client! . . .\n");  
    
	/* Receive the message from the socket
	 */
	memset(recvBuff, '\0', 1025);
	n = read(connfd, recvBuff, 1025);
	if (n >= 0)
	    fprintf (stdout, "Message received(%d): %s\n", n, recvBuff);

	// EXAMPLE: Set value of lights according to message received.
	if ( strcmp(recvBuff, "/help") == 0 ) {
	    this->Help (sendBuff, recvBuff);
	}
	else if ( strcmp(recvBuff, "/list") == 0 ) {
	    this->List (sendBuff, recvBuff);
	}

	else if ( strcmp(recvBuff, "/status") == 0 ) {
	    this->Status (sendBuff, recvBuff);
	}
		
	else if ( strcmp(recvBuff, "/set/room3L/Yeelight/power on") == 0 ) {
	    mosquitto_publish(this->h->mosq, NULL, "/set/room3L/Yeelight/power", strlen("on"), "on", 0, 0);

	}
	else if ( strcmp(recvBuff, "/set/room3L/Yeelight/power off") == 0 ) {
	    mosquitto_publish(this->h->mosq, NULL, "/set/room3L/Yeelight/power", strlen("off"), "off", 0, 0);
	}

	else if ( strcmp(recvBuff, "/lights=on") == 0 ) {
	    strcpy(value, "1\0");
	    mosquitto_publish(this->h->mosq, NULL, "/room1L/lights", strlen(value), value, 0, 0);
	    mosquitto_publish(this->h->mosq, NULL, "/room2R/lights", strlen(value), value, 0, 0);
	    mosquitto_publish(this->h->mosq, NULL, "/room3L/lights", strlen(value), value, 0, 0);
	}
	else if ( strcmp(recvBuff, "/lights=off") == 0 ) {
	    strcpy(value, "0\0");
	    mosquitto_publish(this->h->mosq, NULL, "/room1L/lights", strlen(value), value, 0, 0);
	    mosquitto_publish(this->h->mosq, NULL, "/room2R/lights", strlen(value), value, 0, 0);
	    mosquitto_publish(this->h->mosq, NULL, "/room3L/lights", strlen(value), value, 0, 0);
	}
	else {
	    strcpy(value, "2\0");
	    mosquitto_publish(this->h->mosq, NULL, "/room1L/lights", strlen(value), value, 0, 0);
	    mosquitto_publish(this->h->mosq, NULL, "/room2R/lights", strlen(value), value, 0, 0);
	    mosquitto_publish(this->h->mosq, NULL, "/room3L/lights", strlen(value), value, 0, 0);
	}
	
	/* As soon as server gets a request from client, it prepares the date and time and
	 * writes on the client socket through the descriptor returned by accept()
	 */
//	ticks = time(NULL);
	//snprintf(sendBuff, sizeof(sendBuff), "ESTA ES LA PUTA HORA ACTUAL: %.24s\r\n", ctime(&ticks));
	write(connfd, sendBuff, strlen(sendBuff));
	sleep(1);

	close(connfd);
	sleep(1);
	
    } // while

}
	
void TelegramInterface::Help (char out[], char in[]) {
    /*
        It returns a string containing help information.

        Args:
	    char out[]: String containing the help information
	    char in[]: String containing the input request

        Returns:
            None

        Raises:
            None
    */
    memset(out, '\0', 1025);
    strcpy (out, "iot_master Telegram Interface version 0.1.\n\n");
    strcat (out, "/status - Show all topics from the Home Automation\n");
    strcat (out, "/list - List of all devices at home\n");
    strcat (out, "/help - Show help for the command (this help)\n");
    strcat (out, "/set - Set the value of a topic\n");
    strcat (out, "/view - Show the value of a topic\n");    
    strcat (out, "<topic> - Read the value of the attribute of a topic\n");
    strcat (out, "<topic> <value> - Write the value of a topic\n");
    
    return;

}


void TelegramInterface::List (char out[], char in[]) {
    /*
        Returns a list of sensors (topics in the MQTT Broker).

        Args:
            char out[]: string with values and topics.
	    char in[]: string with incoming request.

        Returns:
            None

        Raises:
            None
    */
    char topics[8192];
	string str;

    memset(out, '\0', 1025);
    memset(topics, '\0', 8192);
    
    // get the list of devices
    str = this->h->printTopics();
    fprintf (stdout, "**** List of Sensors at Home:\n%s\n", str.c_str());

    strcpy (out, str.c_str());
    
    return;

}

void TelegramInterface::Status (char out[], char in[]) {
    /*
        Returns a list of topics to and its values.

        Args:
            char out[]: string with values and topics.
	    char in[]: string with incoming request.

        Returns:
            None

        Raises:
            None
    */
    char topics[8192];
    string str;

    memset(out, '\0', 1025);
    memset(topics, '\0', 8192);
    
    // get the list of devices
    str = this->h->printStatus();
    fprintf (stdout, "**** Status of Sensors at Home:\n%s\n", str.c_str());

    strcpy (out, str.c_str());
    
    return;

}
