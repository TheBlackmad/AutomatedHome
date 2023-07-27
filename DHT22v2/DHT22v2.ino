#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <SimpleDHT.h>
#include "../../Webserver/WebServer/Sensor_Master-v3.h"  // or your location of the Sensor_Master-v3.h file
#include <PubSubClient.h>   // Library to use MQTT Protocol.

// This two #defines are specific for each client.
#define _ID_SENSOR_       "3L"    // XY in form X=0..3 Y=R/L. Change this ID for each individual NodeMCU Board
#define _DEVICE_NAME_     "DHT22"       

DHT22Data dhtData;
String Hostname;

ADC_MODE(ADC_VCC);

WiFiClient client;                           // Initialize the Wi-Fi client library.
SimpleDHT22 dht22(_PIN_DHT_);
PubSubClient mqttClient(client);             // Initialize a second PubSubClient library.

// Bug workaround for Arduino 1.6.6, it seems to need a function declaration
// for some reason (only affects ESP8266, likely an arduino-builder bug).
void reconnect();
 
void setup() {
  long rssi;
  
  // initialize variables
  dhtData.temperature = dhtData.humidity = dhtData.battery = 0.0;
  dhtData.rssi = 0;
  Hostname = _IP_BASE_NAME_;
  Hostname.concat(_ID_SENSOR_);
  
  // initialize UART
  Serial.begin(115200);
  delay(10); 

  // initialize WiFi
  Serial.println();
  Serial.println();

  // Disable the WiFi persistence.  The ESP8266 will not load and save WiFi settings in the flash memory.
  Serial.print("Disable the WiFi persistence . . . ");
  WiFi.forceSleepWake();
  delay( 1 );
  WiFi.persistent( false );
  Serial.println("[ OK ]");
  
  // Configuring an static IP address
  Serial.print("Configuring an static IP address for ");
  Serial.print(Hostname);
  Serial.print(" . . . ");
  WiFi.mode( WIFI_STA );
  WiFi.hostname(Hostname);
  Serial.println("[ OK ]");

  // Establish connection with router
  Serial.print("Connecting to ");
  Serial.print(_SSID_);
  WiFi.begin(_SSID_, _PASSWORD_);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(". ");
  }
  Serial.println("[ OK ]");
  Serial.print("Use this URL to connect: ");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/"); 
  Serial.print("Signal strength (RSSI): ");
  rssi = WiFi.RSSI();
  Serial.print(rssi);
  Serial.println("dBm\n");

} // setup

void loop()
{
  
  // read temperature and humidity
  Serial.println("Reading all sensors data. . .");
  readSampleDHT();

  if ( !mqttClient.connected() ) 
  {
    Serial.print("Attempting MQTT connection...");
    reconnect();
  }

  mqttClient.loop(); // check subscription
  mqttPublish ( String("/room") + _ID_SENSOR_ + "/" + _DEVICE_NAME_ + String("/temperature"), String(dhtData.temperature) );
  mqttPublish ( String("/room") + _ID_SENSOR_ + "/" + _DEVICE_NAME_ + String("/humidity"), String(dhtData.humidity) );
  mqttPublish ( String("/room") + _ID_SENSOR_ + "/" + _DEVICE_NAME_ + String("/battery"), String(dhtData.battery) );
  mqttPublish ( String("/room") + _ID_SENSOR_ + "/" + _DEVICE_NAME_ + String("/rssi"), String(dhtData.rssi) );


  delay(_DEEP_SLEEP_TIME_/1000); // delay argument is in milliseconds

}

//****************************************************************
//****************************************************************
//****************************************************************

void reconnect() 
{

  // Loop until reconnected.
  while (!mqttClient.connected()) 
  {
    // Set Server
    mqttClient.setServer (_MQTT_SERVER_, _MQTT_PORT_);
    
    // Connect to the MQTT broker.
    Serial.print("Attempting MQTT connection as "); 
    Serial.print (Hostname.c_str());
    Serial.println (" . . .");
    if ( mqttClient.connect(Hostname.c_str()) ) 
    {
      Serial.println(" [ OK ]");
    } else 
    {
      Serial.print("failed, rc=");
      // Print reason the connection failed.
      // See https://pubsubclient.knolleary.net/api.html#state for the failure code explanation.
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }

  return;
  
}


// read the sample data for this sensor and all sensors (?)
void readSampleDHT () {
  float t=0.0, h=0.0, rssi=0.0;
  int b=0;
  int tries=0;
  int err = SimpleDHTErrSuccess;
  
  // read without samples.
  // @remark We use read2 to get a float data, such as 10.1*C
  //    if user doesn't care about the accurate data, use read to get a byte data, such as 10*C.
  while (tries <= _SENSORS_TRIES_) {
    if ((err = dht22.read2(&t, &h, NULL)) != SimpleDHTErrSuccess) {
      Serial.print("Read DHT22 failed, err="); Serial.println(err);delay(2000);
      tries++;
    }
    else
      tries = _SENSORS_TRIES_ + 1;
  }

  // read status of the battery
  b = ESP.getVcc();    
  
  Serial.print("Sample OK: ");
  Serial.print((float)t); Serial.print(" *C, ");
  Serial.print((float)h); Serial.println(" RH%");

  // change data for the server sensors (these sensors)
  dhtData.temperature = t;
  dhtData.humidity = h;
  dhtData.battery = (float) (1.0*b) / 1000.0;
  dhtData.rssi = WiFi.RSSI();

  return;

}

void mqttPublish (String topic, String value) {

  const char *msgBuffer, *topicBuffer;
  
 // Create data string to send
  msgBuffer = value.c_str();
  
  // Create a topic string and publish data
  topicBuffer = topic.c_str();
  Serial.print("Topic to Publish: "); Serial.println(topicBuffer);
  Serial.print("Value to Publish: "); Serial.println(msgBuffer);
  if ( mqttClient.publish( topicBuffer, msgBuffer ) ) {
    Serial.println("Published . . . [ OK ]");
  }
  else {
    Serial.println("Published . . . [ ERROR ]");    
  }

  return;
    
}
