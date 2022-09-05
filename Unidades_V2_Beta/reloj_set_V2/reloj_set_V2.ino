/*
   Programa para setear la Hora del modulo DS3231
   Desarrollado por Cristobal Garrido Caceres
   Julio de 2019
   FCFM
*/

#include <DS3231.h>
#include <Wire.h>

DS3231 Clock;
bool Century = false;
bool h12;
bool PM;
bool ADay, AHour, AMinute, ASecond, ABits;
bool ADy, A12h, Apm;
int Jahre, Monate, DatumTag, Wochentag, Uhr, Minuten, Sekunden; // Para los datos recividos
int second, minute, hour, date, month, year;

void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  Serial.begin(115200);
  delay(1000);
  // Time out for introduce automatic value 0
  Serial.setTimeout(60000);
  Serial.println(F("Welcome!"));


  second = Clock.getSecond();
  minute = Clock.getMinute();
  hour = Clock.getHour(h12, PM);
  date = Clock.getDate();
  month = Clock.getMonth(Century);
  year = Clock.getYear();

  Serial.print("20");
  Serial.print(year, DEC);
  Serial.print('-');
  Serial.print(month, DEC);
  Serial.print('-');
  Serial.print(date, DEC);
  Serial.print(' ');
  Serial.print(hour, DEC);
  Serial.print(':');
  Serial.print(minute, DEC);
  Serial.print(':');
  Serial.print(second, DEC);
  Serial.print('\n');

  Serial.println(F("Year? ex. 16"));
  while (1)
  {
    if (Serial.available()>0)
    {
      Jahre = Serial.parseInt();
      if (Jahre > 0)
      {
        Serial.print(F("Year: "));
        Serial.println(Jahre);
        break;
      }
    }
  }

  Serial.println(F("Month?"));
  while (1)
  {
    if (Serial.available()>0)
    {
      Monate = Serial.parseInt() ;
      if (Monate > 0)
      {
        Serial.print(F("Month: "));
        Serial.println(Monate);
        break;
      }
    }
  }

  Serial.println(F("Day?"));
  while (1)
  {
    if (Serial.available()>0)
    {
      DatumTag = Serial.parseInt() ;
      if (DatumTag > 0)
      {
        Serial.print(F("Day: "));
        Serial.println(DatumTag);
        break;
      }
    }
  }
  
  Serial.println(F("Week day? (1) Monday, (2) Tuesday, (3) Wednesday, etc."));
  while (1)
  {
    if (Serial.available()>0)
    {
      Wochentag = Serial.parseInt() ;
      if (Wochentag > 0)
      {
        Serial.print(F("Week day: "));
        Serial.println(Wochentag);
        break;
      }
    }
  }

  Serial.println(F("Hour?"));
  while (1)
  {
    if (Serial.available()>0)
    {
      Uhr = Serial.parseInt();
      if (Uhr >= 0)
      {
        Serial.print(F("Hour: "));
        Serial.println(Uhr);
        break;
      }
    }
  }

  Serial.println(F("Minute?"));
  while (1)
  {
    if (Serial.available()>0)
    {
      Minuten = Serial.parseInt();
      if (Minuten >= 0)
      {
        Serial.print(F("Minute: "));
        Serial.println(Minuten);
        break;
      }
    }
  }
  
  Serial.println(F("Second?"));
  while (1)
  {
    if (Serial.available()>0)
    {
      Sekunden = Serial.parseInt();
      if (Sekunden >= 0)
      {
        Serial.print(F("Second: "));
        Serial.println(Sekunden);
        break;
      }
    }
  }

  Clock.setSecond(Sekunden);//Set the second
  Clock.setMinute(Minuten);//Set the minute
  Clock.setHour(Uhr);  //Set the hour
  Clock.setDoW(Wochentag);    //Set the day of the week
  Clock.setDate(DatumTag);  //Set the date of the month
  Clock.setMonth(Monate);  //Set the month of the year
  Clock.setYear(Jahre);  //Set the year (Last two digits of the year)
  // Start the serial interface
  Serial.println(F("Thank you!"));


}

void loop() {
  // put your main code here, to run repeatedly:
  second = Clock.getSecond();
  minute = Clock.getMinute();
  hour = Clock.getHour(h12, PM);
  date = Clock.getDate();
  month = Clock.getMonth(Century);
  year = Clock.getYear();

  Serial.print("20");
  Serial.print(year, DEC);
  Serial.print('-');
  Serial.print(month, DEC);
  Serial.print('-');
  Serial.print(date, DEC);
  Serial.print(' ');
  Serial.print(hour, DEC);
  Serial.print(':');
  Serial.print(minute, DEC);
  Serial.print(':');
  Serial.print(second, DEC);
  Serial.print('\n');
}
