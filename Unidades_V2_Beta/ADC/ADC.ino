#define SELPIN 4 //Selection Pin 
#define DATAOUT 11//MOSI 
#define DATAIN  12//MISO 
#define SPICLOCK  13//Clock 
//int readvalue0; 
int readvalue1; 
//int readvalue2; 
//int readvalue3; 
void setup(){ 
 //set pin modes 
 pinMode(SELPIN, OUTPUT); 
 pinMode(DATAOUT, OUTPUT); 
 pinMode(DATAIN, INPUT); 
 pinMode(SPICLOCK, OUTPUT); 
 //disable device to start with 
 digitalWrite(SELPIN,HIGH); 
 digitalWrite(DATAOUT,LOW); 
 digitalWrite(SPICLOCK,LOW); 

 Serial.begin(115200); 
} 

int read_adc(int channel){
  int adcvalue = 0;
  byte commandbits = B11000000; //command bits - start, mode, chn (3), dont care (3)

  //allow channel selection
  commandbits|=((channel-1)<<3);

  digitalWrite(SELPIN,LOW); //Select adc
  // setup bits to be written
  for (int i=7; i>=3; i--){
    digitalWrite(DATAOUT,commandbits&1<<i);
    //cycle clock
    digitalWrite(SPICLOCK,HIGH);
    digitalWrite(SPICLOCK,LOW);    
  }

  digitalWrite(SPICLOCK,HIGH);    //ignores 2 null bits
  digitalWrite(SPICLOCK,LOW);
  digitalWrite(SPICLOCK,HIGH);  
  digitalWrite(SPICLOCK,LOW);

  //read bits from adc
  for (int i=11; i>=0; i--){
    adcvalue+=digitalRead(DATAIN)<<i;
    //cycle clock
    digitalWrite(SPICLOCK,HIGH);
    digitalWrite(SPICLOCK,LOW);
  }
  digitalWrite(SELPIN, HIGH); //turn off device
  return adcvalue;
}


void loop() { 
 //Serial.print(millis());
 //Serial.print(F(" "));
 //readvalue0 = read_adc(1); 
 //delay(1);
 readvalue1 = read_adc(2);
 delay(1);
 //readvalue2 = read_adc(3);
 //delay(1);
 //readvalue3 = read_adc(4); 
 //delay(1);

 Serial.print(millis()); 
 //Serial.print(readvalue0,DEC); 
 Serial.print(F(";")); 
 Serial.println(readvalue1,DEC);
 //Serial.print(F(","));
 //Serial.print(readvalue2,DEC);
 //Serial.print(F(","));
 //Serial.println(readvalue3,DEC); 
 //Serial.println(" "); 
} 
