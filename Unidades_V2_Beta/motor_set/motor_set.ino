/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo myservo1;
Servo myservo2;// create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 90;    // variable to store the servo position

void setup() {
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(13, OUTPUT);
  
  digitalWrite(4, HIGH); // Desconexion Motores
  digitalWrite(5, HIGH); // Motor 1
  digitalWrite(6, HIGH); // Motor 2

  myservo1.attach(9); //Inicializamos los motores (1 horizontal / 2 vertical)
  myservo2.attach(10);

}

void loop() {
 
    myservo1.write(pos);              // tell servo to go to position in variable 'pos'
    myservo2.write(pos);              // tell servo to go to position in variable 'pos'
    
}

