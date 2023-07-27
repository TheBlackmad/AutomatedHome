
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

#ifndef __TELEGRAMINTERFACE__
#define __TELEGRAMINTERFACE__

#include <iostream>
#include <string>
#include <mosquitto.h>
#include "autohome.hpp"

// this is for the socket functionality
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <time.h>
#include <errno.h>



// Flags for debug mode: 1 active; 0 inactive
#define _TI_DEBUG_				1
#define _TI_PORT_				12350

class AutomatedHome;

class TelegramInterface {

	private:
	AutomatedHome *h;

	public:
	// methods
	TelegramInterface(AutomatedHome *h);
	~TelegramInterface();
	void telegramServer(void);

	private:
	void Help (char out[], char in[]);
	void List (char out[], char in[]);
	void Status (char out[], char in[]);

};

#endif
