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
  myservo3.write(0);
  myservo4.write(0);

  // Menampilkan pesan instruksi di Serial Monitor
  Serial.println("Kontrol Servo Siap.");
  Serial.println("Kirim perintah dengan format: S<nomor_servo>,<posisi>");
  Serial.println("Contoh: S9,90 atau S12,45");
  Serial.println("Kirim 'default' untuk reset semua servo ke posisi awal");
}

// Fungsi untuk reset servo ke posisi awal
void resetToDefault()
{
  myservo1.write(0);
  myservo2.write(0);
  myservo3.write(0);
  myservo4.write(0);
  Serial.println("Semua servo direset ke posisi awal");
}

void loop()
{
  // Cek apakah ada data yang masuk dari Serial Monitor
  if (Serial.available() > 0)
  {
    // Baca string yang masuk sampai karakter newline
    String command = Serial.readStringUntil('\n');
    command.trim(); // Hapus spasi atau karakter tak terlihat

    // Cek apakah perintah adalah "default"
    if (command.equalsIgnoreCase("default"))
    {
      resetToDefault();
      return;
    }

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
        Serial.println("Nomor servo tidak valid. Gunakan 9-12.");
        break;
      }
    }
    else
    {
      Serial.println("Format perintah salah. Contoh: S9,90");
    }
  }
}