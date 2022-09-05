/*
   Programa para setear la Hora del modulo DS3231
   Desarrollado por Cristobal Garrido Caceres
   Febrero de 2017
   FCFM-MCI
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

void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  Serial.begin(115200);
  delay(1000);
  Serial.println(F("Herzlich Willkomen!"));

  Serial.println(F("Jahre? z.b. 16"));
  while (1)
  {
    if (Serial.available() > 0)
    {
      Jahre = Serial.parseInt();
      Serial.print(F("Jahre: "));
      Serial.println(Jahre);
      break;
    }
  }

  Serial.println(F("Monate?"));
  while (1)
  {
    if (Serial.available() > 0)
    {
      Monate = Serial.parseInt() ;
      Serial.print(F("Monate: "));
      Serial.println(Monate);
      break;
    }
  }

  Serial.println(F("Datum Tag?"));
  while (1)
  {
    if (Serial.available() > 0)
    {
      DatumTag = Serial.parseInt() ;
      Serial.print(F("Datum tag: "));
      Serial.println(DatumTag);
      break;
    }
  }
  delay(1000);

  Serial.println(F("Wochentag? (1) Montag, (2) Dienstag, (3) Mittwoch, usw."));
  while (1)
  {
    if (Serial.available() > 0)
    {
      Wochentag = Serial.parseInt() ;
      Serial.print(F("Wochentag: "));
      Serial.println(Wochentag);
      break;
    }
  }

  Serial.println(F("Uhr?"));
  while (1)
  {
    if (Serial.available() > 0)
    {
      Uhr = Serial.parseInt();
      Serial.print(F("Uhr: "));
      Serial.println(Uhr);
      break;
    }
  }

  Serial.println(F("Minuten?"));
  while (1)
  {
    if (Serial.available() > 0)
    {
      Minuten = Serial.parseInt();
      Serial.print(F("Minuten: "));
      Serial.println(Minuten);
      break;
    }
  }

  Serial.println(F("Sekunden?"));
  while (1)
  {
    if (Serial.available() > 0)
    {
      Sekunden = Serial.parseInt();
      Serial.print(F("Sekunden: "));
      Serial.println(Sekunden);
      break;
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
  Serial.println(F("Vielen Dank!"));


}

void loop() {
  // put your main code here, to run repeatedly:
  int second, minute, hour, date, month, year;
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

