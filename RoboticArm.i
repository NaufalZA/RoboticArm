#include <Servo.h>

// Servo objects
Servo servo9;   // Pin 9: 0-180 degrees
Servo servo10;  // Pin 10: 0-180 degrees  
Servo servo11;  // Pin 11: 15-45 degrees
Servo servo12;  // Pin 12: 0-180 degrees

void setup() {
  Serial.begin(9600);
  Serial.println("Starting 4 Servo Test");
  
  // Attach servos to pins
  servo9.attach(9);
  servo10.attach(10);
  servo11.attach(11);
  servo12.attach(12);
  
  // Move to initial positions
  servo9.write(0);
  servo10.write(0);
  servo11.write(15);
  servo12.write(0);
  
  delay(1000);
}

void loop() {
  Serial.println("Testing all servos - Forward direction");
  
  // Move all servos to maximum positions
  for(int pos = 0; pos <= 180; pos += 2) {
    if(pos <= 180) servo9.write(pos);        // 0-180
    if(pos <= 180) servo10.write(pos);       // 0-180
    if(pos >= 15 && pos <= 45) servo11.write(pos);  // 15-45
    if(pos <= 180) servo12.write(pos);       // 0-180
    
    delay(20);
  }
  
  delay(1000);
  Serial.println("Testing all servos - Reverse direction");
  
  // Move all servos back to minimum positions
  for(int pos = 180; pos >= 0; pos -= 2) {
    if(pos >= 0) servo9.write(pos);          // 180-0
    if(pos >= 0) servo10.write(pos);         // 180-0
    if(pos >= 15 && pos <= 45) servo11.write(pos);  // 45-15
    if(pos >= 0) servo12.write(pos);         // 180-0
    
    delay(20);
  }
  
  delay(1000);
}
