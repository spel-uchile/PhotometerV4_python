/* ==================================================================================
  File:          Full_V5_prev.ino
  Author:  MCI Electronics / Space and Planetary Exploration Laboratory
                www.olimex.cl / www.spel.uchile.cl 
  Description:   Example source code for Automatic Photometer Sensor Managment
  Target Device: Arduino Uno
  ==================================================================================
  //  Ver | dd mmm yyyy | Author  | Description
  // =====|=============|========|=====================================================
  // 1.00 | 25 Ene 2016 | CGC   | First release
  // ==================================================================================*/


// Si no tienes estas librerías las descargas y las agregas a la carpeta de librerías de Arduino
#include <SFE_BMP180.h> // BMP 180 Para barometro, altura y presion
#include <Wire.h> // Comunicacion I2C
#include <TinyGPS++.h> // Libreria del GPS
#include <SoftwareSerial.h> // Libreria para crear puertos seriales
#include <SD.h> // Libreria para tarjeta SD

const int chipSelect = 6; // SS tarjeta SD
char ID[] = "001"; // ID del instrumento
static const int RXPin = 8, TXPin = 9; // Pines serial para el GPRS
static const uint32_t GPSBaud = 9600; // Velocidad de conexion GPRS
char dato;

SFE_BMP180 pressure; // Objeto BMP
TinyGPSPlus gps; // Objeto GPS
SoftwareSerial GPRSBee(3, 2); // Conexion serial paraconectarse al GPRS
SoftwareSerial ss(RXPin, TXPin); // Conexion serial para conectarse al GPS


#define SELPIN 4 //Pin de activación del ADC
#define DATAOUT 11 // MOSI
#define DATAIN 12 // MISO
#define SPICLOCK 13 // CLK
#define CTRL_Z 26 // termino


void setup()
{
  String zz, zz2, zz3, zz4;

  // Inicialización ADC
  //set pin modes
  pinMode(SELPIN, OUTPUT);
  pinMode(DATAOUT, OUTPUT);
  pinMode(DATAIN, INPUT);
  pinMode(SPICLOCK, OUTPUT);
  //disable device to start with
  digitalWrite(SELPIN, HIGH);
  digitalWrite(DATAOUT, LOW);
  digitalWrite(SPICLOCK, LOW);


  // Pin que enciende el módulo GPRS
  pinMode(7, OUTPUT);
  digitalWrite(7, LOW);

  //Señal proveniente del arduino por mini
  pinMode(A2,INPUT);
  // Inicialización de comunicaciones seriales y BMP
  Serial.begin(9600);
  ss.begin(GPSBaud);
  pressure.begin();

  //--------------------Medicion-----------------------------
  //Sensores
  zz = ID;
  while (digitalRead(A2)== 0)
  {
    //Serial.println(digitalRead(A2));
  }
  delay(100);
  //Serial.println("OK");
  zz2 = data();

  //Serial.println(millis());
  //ahora esperamos y mandamos los datos
  delay(100);
  zz3 = GPS();
  delay(100);

  GPRSBee.begin(9600);
  SD.begin(6);

  delay(100);
  zz4 = BMP();
  delay(100);


  // Encendiendo y configurando el módulo GPRS
//Serial.println(F("Encendiendo Modem"));
//  ModemOn();
//  delay(2000);
//  Serial.println(F("Configurando Modem"));
//  configuracionGPRSBee();
//  delay(10000);

  // Se conecta y comienza a enviar los datos

//  SendData(zz, zz2, zz3, zz4);

  // Guardando datos en la micro SD
  File dataFile = SD.open("Data.txt", FILE_WRITE);
  // Si el archivo está disponible se guardan los datos
  if (dataFile) {
    dataFile.print(zz);
    dataFile.print(zz2);
    dataFile.print(zz3);
    dataFile.println(zz4);
    dataFile.close();
    // imprimiendo el puerto serial
//    Serial.println(zz + zz2 + zz3 + zz4);
  }
  // En el caso de no disponibilidad avisa el error
  else {
    //Serial.println(F("Error en Data.txt"));
  }
  delay(100);
  //Informamos termino de la medicion
  //digitalWrite(A2, HIGH);
//  Serial.println(millis());
}

void loop()
{
}



//----------------------Obtencion datos sensores---------------------------

String data()
{
  const char coma = ',';
  int readvalue;
  int data1, data2, data3, data4;
  String zz;
  unsigned long tiempo;
  //coma = ","; // Separador reservado para ahorrar memoria
  //P0 = 1013; // Persión al nivel del mar
  tiempo = millis(); //El tiempo de incicio para marcar
  data1 = 0;
  data2 = 0;
  data3 = 0;
  data4 = 0;
  //Sensores
  while (digitalRead(A2))
  {
    readvalue = read_adc(1);

    if (data1 <= readvalue)
    {
      data1 = readvalue;
    }

    readvalue = read_adc(2);

    if (data2 <= readvalue)
    {
      data2 = readvalue;
    }
    readvalue = read_adc(3);

    if (data3 <= readvalue)
    {
      data3 = readvalue;
    }

    readvalue = read_adc(4);

    if (data4 <= readvalue)
    {
      data4 = readvalue;
    }
  }
  zz = coma;
  zz += data1;
  zz += coma;
  zz += data2;
  zz += coma;
  zz += data3;
  zz += coma;
  zz += data4;
//Serial.println(zz);
  return zz;
}

//-------------------------Obtencion datos GPS----------------------------
String GPS()
{
  const char coma = ',';
  String zz;
  unsigned long tiempo;
  boolean latlong, diamesagno, hrminseg, alt;
  latlong = false;
  diamesagno = false;
  hrminseg = false;
  alt = false;

  tiempo = millis(); //El tiempo de incicio para marcar

  while (millis() < tiempo + 30000)
  {
    while (ss.available() > 0)
    {
      //Serial.print(F("Location: "));
      if (gps.encode(ss.read()))
      {
        if (gps.location.isValid() && latlong)
        {
          latlong = true;
        }

        if (gps.date.isValid())
        {
          diamesagno = true;
        }
        if (gps.time.isValid())
        {
          hrminseg = true;
        }
        //Serial.print(F(","));
        if (gps.altitude.isValid())
        {
          alt = true;
        }
        if (latlong && diamesagno && hrminseg && alt)
        {
          break;
        }
      }
    }
  }
  if (latlong)
  {
    zz = coma;
    zz += gps.location.lat();
    zz += coma;
    zz += gps.location.lng();
  }
  else
  {
    zz = coma;
    zz += coma;
  }

  //, Dia, Mes, Agno
  if (diamesagno)
  {
    zz += coma;
    zz += gps.date.day();
    zz += coma;
    zz += gps.date.month();
    zz += coma;
    zz += gps.date.year();

  }
  else
  {
    zz += coma;
    zz += coma;
    zz += coma;
  }

  //, Hora, Minuto, Segundo
  if (hrminseg)
  {
    zz += coma;
    zz += gps.time.hour();
    zz += coma;
    zz += gps.time.minute();
    zz += coma;
    zz += gps.time.second();
  }
  else
  {
    zz += coma;
    zz += coma;
    zz += coma;
  }

  //, Altura_GPS
  if (alt)
  {
    zz += coma;
    zz += gps.altitude.meters();
  }
  else
  {
    zz += coma;
  }
  return zz;
}

//-----------------------Obtencion datos BMP---------------------------
String BMP()
{
  char status;
  const char coma = ',';
  String zz;
  double T, P, a;
  //,Temperatura
  status = pressure.startTemperature();
  if (status != 0)
  {
    delay(status);
    status = pressure.getTemperature(T);
  }
  if (status != 0)
  {
    zz = coma;
    zz += T;

    //, Presion, Altura_BMP
    status = pressure.startPressure(3);
  }
  else
  {
    zz = coma;
  }

  if (status != 0)
  {
    delay(status);

    status = pressure.getPressure(P, T);
    if (status != 0)
    {
      const int P0 = 1013;
      zz += coma;
      zz += P;

      a = pressure.altitude(P, P0);
      zz += coma;
      zz += a;
    }
  }
  else
  {
    zz += coma;
    zz += coma;
  }
  return zz;
}
//--------------Loop para leer datos de módulo GPRS--------------------------------------------------------------
int serial()
{
  while (Serial.available() != 0)
  {
    dato = Serial.read();
    GPRSBee.print(dato);
  }
  while (GPRSBee.available() != 0)
  {
    dato = GPRSBee.read();
    Serial.print(dato);
  }
}
//-----------Configuracion de módulo GPRS--------------------------------------------------------------------------
int configuracionGPRSBee()
{

  SendCommand(F("AT"), 2000, 3);
  SendCommand(F("AT+CMEE=2"), 2000, 3);
  SendCommand(F("AT+QICSGP=1,\"web.tmovil.cl\""), 3000, 3); // APN. En este caso tiene la APN de Movistar
  SendCommand(F("AT+QIHEAD=1"), 3000, 3);
  SendCommand(F("AT+QIDNSIP=1"), 3000, 3);
  SendCommand(F("AT&W"), 2000, 3);

}

//------String envio de datos por módulo GPRS----------------------------------------------------------------------
int SendData(String zz, String zz2, String zz3, String zz4)
{
  SendCommand(F("AT+QIOPEN=\"TCP\",\"wfgarrido.ddns.net\",\"25565\""), 3000, 3);  // Dirección y puerto
  delay(4000);
  serial();
  SendCommand(F("AT+QISEND"), 100, 1);
  GPRSBee.print(zz);
  GPRSBee.print(zz2);
  GPRSBee.print(zz3);
  GPRSBee.println(zz4);
  GPRSBee.write(CTRL_Z);
  GPRSBee.println(F("AT+QICLOSE"));
  delay(500);
  serial();
}

//------ModemOn-------------------------------------------------------------------------------------------------------
void ModemOn() {
  unsigned long time_1;
  unsigned long time_2;
  boolean estado_modem = false;
  char recibido;

  time_1 = millis() + 4000;
  time_2 = millis();
  GPRSBee.flush();
  GPRSBee.println("AT");
  while ((GPRSBee.available() > 0 || time_1 > time_2) && estado_modem == false)
  {
    time_2 = millis();
    if (GPRSBee.available() >= 0)
    {
      recibido = GPRSBee.read();
      if (recibido == 'K')
      {
        estado_modem = true;
      }
    }
  }
  if (estado_modem == false)
  {
    digitalWrite(7, LOW);
    delay(1000);
    digitalWrite(7, HIGH);
    delay(1000);
    digitalWrite(7, LOW);
    delay(5000);
  }
  serial();
}

//------Envío de comando------------------------------------------------------------------------------------------------
boolean SendCommand(String command, int time, int repeat)
{
  unsigned long time_1;
  unsigned long time_2;
  boolean respuesta_modem = false;
  char recibido;
  int x = 0;

  while ( x < repeat && respuesta_modem == false)
  {
    time_1 = millis() + time;
    time_2 = millis();

    Serial.println(command);
    GPRSBee.println(command);

    while ((GPRSBee.available() > 0 || time_1 > time_2) && respuesta_modem == false)
    {

      time_2 = millis();
      if (GPRSBee.available() >= 0)
      {
        recibido = GPRSBee.read();
        //Serial.println(recibido);
        if (recibido == 'K')
        {
          respuesta_modem = true;
          Serial.println(F("OK"));
        }
      }
    }
    x++;
  }
  return respuesta_modem;
}

//-------------------------Lectura de datos desde ADC------------------------

int read_adc(int channel) {
  int adcvalue = 0;
  byte commandbits = B11000000; //command bits - start, mode, chn (3), dont care (3)

  //allow channel selection
  commandbits |= ((channel - 1) << 3);

  digitalWrite(SELPIN, LOW); //Select adc
  // setup bits to be written
  for (int i = 7; i >= 3; i--) {
    digitalWrite(DATAOUT, commandbits & 1 << i);
    //cycle clock
    digitalWrite(SPICLOCK, HIGH);
    digitalWrite(SPICLOCK, LOW);
  }

  digitalWrite(SPICLOCK, HIGH);   //ignores 2 null bits
  digitalWrite(SPICLOCK, LOW);
  digitalWrite(SPICLOCK, HIGH);
  digitalWrite(SPICLOCK, LOW);

  //read bits from adc
  for (int i = 11; i >= 0; i--) {
    adcvalue += digitalRead(DATAIN) << i;
    //cycle clock
    digitalWrite(SPICLOCK, HIGH);
    digitalWrite(SPICLOCK, LOW);
  }
  digitalWrite(SELPIN, HIGH); //turn off device
  return adcvalue;
}

