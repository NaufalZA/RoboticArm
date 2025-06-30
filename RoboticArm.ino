#include <Servo.h>

#define ServoPort1 9
#define ServoPort2 10
#define ServoPort3 11
#define ServoPort4 12

// Servo range definitions [min, max]
int servoRanges[4][2] = {
    {0, 180}, // Servo 9 range: tangan kiri
    {0, 180}, // Servo 10 range: bawah
    {55, 80}, // Servo 11 range: capit
    {0, 180}  // Servo 12 range: tangan kanan
};

int defaultPositions[4] = {90, 90, 70, 90}; // Default positions for each servo

Servo myservo1, myservo2, myservo3, myservo4;

void setup()
{
  Serial.begin(115200);

  myservo1.attach(ServoPort1);
  myservo2.attach(ServoPort2);
  myservo3.attach(ServoPort3);
  myservo4.attach(ServoPort4);

  // Set to default positions
  myservo1.write(defaultPositions[0]);
  myservo2.write(defaultPositions[1]);
  myservo3.write(defaultPositions[2]);
  myservo4.write(defaultPositions[3]);

  Serial.println("Started");
}

void resetToDefault()
{
  myservo1.write(defaultPositions[0]);
  myservo2.write(defaultPositions[1]);
  myservo3.write(defaultPositions[2]);
  myservo4.write(defaultPositions[3]);
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

      // Apply servo-specific constraints
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