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

const int chipSelect = 8; // SS tarjeta SD
char ID[] = "007"; // ID del instrumento
static const uint32_t GPSBaud = 9600; // Velocidad de conexion GPS
char dato;

SFE_BMP180 pressure; // Objeto BMP
TinyGPSPlus gps; // Objeto GPS
SoftwareSerial ss(3, 2); // Conexion serial para conectarse al GPS


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
    
  }
  
  delay(100);
  zz2 = data();

  //ahora esperamos y mandamos los datos
  delay(100);
  zz3 = GPS();
  delay(100);

  SD.begin(8);
  delay(100);
  
  zz4 = BMP();
  delay(100);

  // Guardando datos en la micro SD
  File dataFile = SD.open("Data.txt", FILE_WRITE);
  // Si el archivo está disponible se guardan los datos
  if (dataFile) {
    dataFile.print(zz);
    dataFile.print(zz2);
    dataFile.print(zz3);
    dataFile.println(zz4);
    dataFile.close();
  }
  // En el caso de no disponibilidad avisa el error
  else {
    //Serial.println(F("Error en Data.txt"));
  }
  delay(100);
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

