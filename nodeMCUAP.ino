#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <Servo.h>

#include "WebHtml.h";

#define ServoPort1 D1
#define ServoPort2 D2
#define ServoPort3 D3
#define ServoPort4 D4

const char* ssid = "Ge Creative";
const char* password = "gecreative";

Servo myservo1, myservo2, myservo3, myservo4;
ESP8266WebServer server(80);

void handleRoot() {
 //String s = MAIN_page; //Read HTML contents
 //server.send(200, "text/html", s); //Send web page

  server.send(200, "text/html", MAIN_page); //--> Send web page
}

void handleServo(){
  String POS1 = server.arg("servoPOS1");
  int pos1 = POS1.toInt();
  myservo1.write(pos1);
  
  String POS2 = server.arg("servoPOS2");
  int pos2 = POS2.toInt();
  myservo2.write(pos2);

  String POS3 = server.arg("servoPOS3");
  int pos3 = POS3.toInt();
  myservo3.write(pos3);

  String POS4 = server.arg("servoPOS4");
  int pos4 = POS4.toInt();
  myservo4.write(pos4);
  
  delay(15);
  server.send(200, "text/plane","");
}

void setup() {
  Serial.begin(115200);
  delay(500);

  myservo1.attach(ServoPort1);
  myservo2.attach(ServoPort2);
  myservo3.attach(ServoPort3);
  myservo4.attach(ServoPort4);
  
  WiFi.softAP(ssid, password);

  IPAddress apip = WiFi.softAPIP();
  Serial.print("Connect your wifi laptop/mobile phone to this NodeMCU Access Point : ");
  Serial.println(ssid);
  Serial.print("Visit this IP : ");
  Serial.print(apip);
  Serial.println(" in your browser.");
  
  server.on("/",handleRoot);
  server.on("/setPOS",handleServo);
  server.begin();  
  Serial.println("HTTP server started");
}

void loop() {
 server.handleClient();
}
