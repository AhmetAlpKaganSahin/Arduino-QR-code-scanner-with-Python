#include <Servo.h>  // Servo motor için kütüphane

Servo myServo;      // Servo motor nesnesi
const int ledPin = 13; // LED için pin numarası (yerleşik LED)

void setup() {
  Serial.begin(9600);   // Seri iletişim başlatılıyor
  myServo.attach(9);    // Servo motoru dijital pin 9'a bağla
  pinMode(ledPin, OUTPUT); // LED pinini çıkış olarak ayarla
  myServo.write(0);      // Servo motor başlangıç pozisyonu
}

void loop() {
  // Seri porttan gelen veriyi kontrol et
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Komut al

    // Eğer gelen komut "UNLOCK" ise kapıyı aç
    if (command == "UNLOCK") {
      Serial.println("Kapı açılıyor!"); // Durum mesajı gönder
      digitalWrite(ledPin, HIGH);      // LED'i yak
      myServo.write(90);               // Servo motoru 90 derece döndür (kapıyı aç)

      delay(5000);                     // 5 saniye bekle
      digitalWrite(ledPin, LOW);       // LED'i kapat
      myServo.write(0);                // Servo motoru başlangıç pozisyonuna getir (kapıyı kapat)
    }
  }
}
