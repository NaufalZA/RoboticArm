#include <Servo.h>

#define ServoPort1 9
#define ServoPort2 10
#define ServoPort3 11
#define ServoPort4 12

Servo myservo1, myservo2, myservo3, myservo4;

void setup()
{
  Serial.begin(11500);

  myservo1.attach(ServoPort1);
  myservo2.attach(ServoPort2);
  myservo3.attach(ServoPort3);
  myservo4.attach(ServoPort4);

  myservo1.write(0);
  myservo2.write(0);
  myservo3.write(0);
  myservo4.write(0);

  Serial.println("Started");
}

void resetToDefault()
{
  myservo1.write(0);
  myservo2.write(0);
  myservo3.write(0);
  myservo4.write(0);
}

void loop()
{
  if (Serial.available() > 0)
  {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equalsIgnoreCase("default"))
    {
      resetToDefault();
      return;
    }

    int commaIndex = command.indexOf(',');

    if (command.startsWith("S") && commaIndex > 0)
    {
      int servoNumber = command.substring(1, commaIndex).toInt();
      int position = command.substring(commaIndex + 1).toInt();

      position = constrain(position, 0, 180);

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