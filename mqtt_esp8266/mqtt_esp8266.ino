/*
 Basic ESP8266 MQTT example

 This sketch demonstrates the capabilities of the pubsub library in combination
 with the ESP8266 board/library.

 It connects to an MQTT server then:
  - publishes "hello world" to the topic "outTopic" every two seconds
  - subscribes to the topic "inTopic", printing out any messages
    it receives. NB - it assumes the received payloads are strings not binary
  - If the first character of the topic "inTopic" is an 1, switch ON the ESP Led,
    else switch it off

 It will reconnect to the server if the connection is lost using a blocking
 reconnect function. See the 'mqtt_reconnect_nonblocking' example for how to
 achieve the same result without blocking the main loop.

 To install the ESP8266 board, (using Arduino 1.6.4+):
  - Add the following 3rd party board manager under "File -> Preferences -> Additional Boards Manager URLs":
       http://arduino.esp8266.com/stable/package_esp8266com_index.json
  - Open the "Tools -> Board -> Board Manager" and click install for the ESP8266"
  - Select your ESP8266 in "Tools -> Board"

*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define LED1 13
#define HIGH_INTENSITY 1024
#define LOW_INTENSITY 128
#define TIMEOUT 8000


// Update these with values suitable for your network.

const char* ssid = "ADAX-Training";
const char* password = "ADAX@Traning-L27";
const char* mqtt_server = "10.100.16.214";

const char* pubTopic = "/nodemcu/general";
const char* subTopic = "/nodemcu/led";


WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0; 

void setup() {
  pinMode(LED1, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  analogWrite(LED1, 512);
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  
  if ((char)payload[0] == 'D') {
    if((char)payload[1] == '1'){
        Serial.println("Brighten up!");
        client.publish(pubTopic, "Notification received, turning up the LED!");
        
        analogWrite(LED1, HIGH_INTENSITY);
      }
     else if ((char)payload[1] == '2') {
        Serial.println("Dimming down!");
        client.publish(pubTopic, "Notification received, dimming down the LED!");
        
        analogWrite(LED1, LOW_INTENSITY);
     }
  }
/*
  // Switch on the LED if an 1 was received as first character
  if ((char)payload[0] == '1') {
    analogWrite(LED1, 1024);   // Turn the LED on (Note that LOW is the voltage level
    // but actually the LED is on; this is because
    // it is acive low on the ESP-01)
    client.publish("isSend", "True");
    client.publish("outTopic", "Signal is On");
    client.publish("halloWorld", "Hallo World");
  } else {
    client.publish("isSend", "True");
    analogWrite(LED1, 512);  // Turn the LED off by making the voltage HIGH
    client.publish("outTopic", "Signal is off");
  }
*/
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish(pubTopic, "Hello world from NodeMCU!");
      // ... and resubscribe
      client.subscribe(subTopic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
