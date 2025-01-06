#include <Servo.h>
#include <Arduino.h>

Servo x;    
Servo y1;   
Servo y2;  
Servo leftClaw; //this is supposed to be the right claw
Servo rightClaw; //this is supposed to be the left claw
int Xangle;  
int Yangle;   
int Tangle;
int Iangle;
const int threshold = 5;

void setup() {
  Serial.begin(9600); 
  x.attach(9);        
  y1.attach(10);     
  y2.attach(11);
  leftClaw.attach(12);
  rightClaw.attach(13); 
  y1.write(90);     
  y2.write(0); 
  leftClaw.write(90);
  rightClaw.write(0); 
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');  //We read the string until the end of the line

    int xIndex = input.indexOf('X'); //All of the possible indexes
    int yIndex = input.indexOf('Y');
    int tIndex = input.indexOf('T');
    int iIndex = input.indexOf('I');

    if (xIndex != -1 && yIndex != -1 && tIndex != -1 && iIndex != -1) {
      Xangle = input.substring(xIndex + 1, yIndex).toInt(); //Read the string from the angle index to the index of the next angle and convert that to an integer (e.g. X45Y <-- we take the input from X to Y and convert it to a number. We get 45)
      Yangle = input.substring(yIndex + 1, tIndex).toInt();
      Tangle = input.substring(tIndex + 1, iIndex).toInt();
      Iangle = input.substring(iIndex + 1).toInt();

      if (Xangle >= 0 && Xangle <= 180) { 
        x.write(180-Xangle); 
      }
      if (Yangle >= 0 && Yangle <= 90) { 
        y1.write(90 - Yangle); 
        y2.write(Yangle);      
      }

      // Control claws based on thumb and index finger positions
      if (Tangle >= 0 && Tangle <= 90 && Iangle >= 0 && Iangle <= 90) {
        // Check if thumb and index finger are close together
        if (abs(Tangle - Iangle) < threshold) {
          leftClaw.write(90);
          rightClaw.write(0);
        } else {
          leftClaw.write(0);
          rightClaw.write(90);
        }
      }
    }
  }
}