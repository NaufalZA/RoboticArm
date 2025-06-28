#include <Servo.h>

#define ServoPort1 9
#define ServoPort2 10
#define ServoPort3 11
#define ServoPort4 12

// Membuat objek untuk setiap servo
Servo myservo1, myservo2, myservo3, myservo4;

void setup()
{
  // Mulai komunikasi serial pada baud rate 9600
  Serial.begin(9600);

  // Menghubungkan objek servo ke pin yang ditentukan
  myservo1.attach(ServoPort1);
  myservo2.attach(ServoPort2);
  myservo3.attach(ServoPort3);
  myservo4.attach(ServoPort4);

  // Mengatur posisi awal servo (90 derajat)
  myservo1.write(0);
  myservo2.write(0);
  myservo3.write(100);
  myservo4.write(60);

  // Menampilkan pesan instruksi di Serial Monitor
  Serial.println("Kontrol Servo Siap.");
  Serial.println("Kirim perintah dengan format: S<nomor_servo>,<posisi>");
  Serial.println("Contoh: S1,90 atau S4,45");
}

void loop()
{
  // Cek apakah ada data yang masuk dari Serial Monitor
  if (Serial.available() > 0)
  {
    // Baca string yang masuk sampai karakter newline
    String command = Serial.readStringUntil('\n');
    command.trim(); // Hapus spasi atau karakter tak terlihat

    // Cari posisi koma sebagai pemisah
    int commaIndex = command.indexOf(',');

    // Pastikan formatnya benar (harus ada 'S' di awal dan ada koma)
    if (command.startsWith("S") && commaIndex > 0)
    {
      // Ambil nomor servo (karakter setelah 'S')
      int servoNumber = command.substring(1, commaIndex).toInt();

      // Ambil nilai posisi (angka setelah koma)
      int position = command.substring(commaIndex + 1).toInt();

      // Batasi nilai posisi antara 0 dan 180
      position = constrain(position, 0, 180);

      Serial.print("Menggerakkan Servo ");
      Serial.print(servoNumber);
      Serial.print(" ke posisi ");
      Serial.println(position);

      // Kirim perintah ke servo yang sesuai
      switch (servoNumber)
      {
      case 1:
        myservo1.write(position);
        break;
      case 2:
        myservo2.write(position);
        break;
      case 3:
        myservo3.write(position);
        break;
      case 4:
        myservo4.write(position);
        break;
      default:
        Serial.println("Nomor servo tidak valid. Gunakan 1-4.");
        break;
      }
    }
    else
    {
      Serial.println("Format perintah salah. Contoh: S1,90");
    }
  }
}