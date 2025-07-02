#include <Servo.h>

#define ServoPort1 9
#define ServoPort2 10
#define ServoPort3 11
#define ServoPort4 12

int servoRanges[4][2] = {
    {0, 180},
    {0, 180},
    {0, 180},
    {0, 180}};

int defaultPositions[4] = {90, 90, 35, 40};

Servo myservo1, myservo2, myservo3, myservo4;

void setup()
{
  Serial.begin(115200);

  myservo1.attach(ServoPort1);
  myservo2.attach(ServoPort2);
  myservo3.attach(ServoPort3);
  myservo4.attach(ServoPort4);

  myservo1.write(defaultPositions[0]);
  myservo2.write(defaultPositions[1]);
  myservo3.write(defaultPositions[2]);
  myservo4.write(defaultPositions[3]);

  Serial.println("Started");
}

void loop()
{
  if (Serial.available() > 0)
  {
    String command = Serial.readStringUntil('\n');
    command.trim();

    int commaIndex = command.indexOf(',');

    if (command.startsWith("S") && commaIndex > 0)
    {
      int servoNumber = command.substring(1, commaIndex).toInt();
      int position = command.substring(commaIndex + 1).toInt();

      int servoIndex = servoNumber - 9;
      if (servoIndex >= 0 && servoIndex < 4)
      {
        position = constrain(position, servoRanges[servoIndex][0], servoRanges[servoIndex][1]);
      }

      switch (servoNumber)
      {
      case 9:
        myservo1.write(position);
        break;
      case 10:
        myservo2.write(position);
        break;
      case 11:
        myservo3.write(position);
        break;
      case 12:
        myservo4.write(position);
        break;
      default:
        break;
      }
    }
  }
}