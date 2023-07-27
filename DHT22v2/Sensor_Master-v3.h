#define _NUM_SENSORS_     8
#define _IDX_0R_          0
#define _IDX_0L_          1
#define _IDX_1R_          2
#define _IDX_1L_          3
#define _IDX_2R_          4
#define _IDX_2L_          5
#define _IDX_3R_          6
#define _IDX_3L_          7
#define _IDX_MASTER_      3
#define _IP_BASE_NUM_	  240		// this is the base IP Address from which the sensors start.
#define _IP_BASE_NAME_	  "IoT-DHT-"	// All devices' names are IoT-DHT-XX, where XX is the index number and R/L for right/left.

#define _WIFI_PORT_       55555
#define _PIN_DHT_         13
#define _DEEP_SLEEP_TIME_ 900e6    	// in microseconds (1e6 = 1sec) -> Typical value 600e6 (10 minute)
// for deep sleep we need to connect GPIO16(D0) to reset also.
#define _PING_TOLERANCE_  10800e3   	// in milliseconds (1e3 = 1sec) -> Typical value 3600e3 (60 minutes)
#define _MAX_ULONG_       4294967295	// that is the max value for a unsigned long
#define _SENSORS_TRIES_   5
#define _MAX_STR_LEN_	  64

#define _NO_TEMP_         -273.0
#define _NO_HUMI_         -100.0
#define _NO_BATT_	   0.0
#define _NO_IP_	   "-.-.-.-"
#define _NO_DEVICE_NAME_   "----"

// Replace with your network credentials
#define _SSID_                "<your SSID>"
#define _PASSWORD_            "<your Password>"
#define _SERVERNAME_          "http://IoT-DHT-Master"
#define _SERVER_SETPRG_NAME_  "/setData"
#define _SERVER_GETPRG_NAME_  "/getData"

// MQTT Server
#define _MQTT_SERVER_		"<your MQQT Server>"
#define _MQTT_PORT_		<your MQTT Server port>

typedef struct _dht22_ {
  float temperature;
  float humidity;
  float battery;
  long rssi;
} DHT22Data;

