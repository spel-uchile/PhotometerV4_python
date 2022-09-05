//Programa Unidad 10
#include <avr/sleep.h> // Libreria para Sleep
#include <DS3231.h> // Libreria reloj con alarma
#include <Wire.h> // Libreria control I2C
#include <Herkulex.h>

//Declaracion Reloj
DS3231 Clock;
// Variables del reloj
byte A1Day, A1Hour, A1Minute, A1Second, AlarmBits;
bool A1Dy, A1h12, A1PM;

bool Century = false;
bool h12;
bool PM;
byte ADay, AHour, AMinute, ASecond, ABits;
bool ADy, A12h, Apm;
float second, minute, hour, day, month, year;

//Pin usado para depertarse
int wakePin = 2;                 // pin used for waking up
int sleepStatus = 0;             // variable to store a request for sleep
int count = 0;                   // counter

//If you live in the southern hemisphere, it would probably be easier
//for you if you make north as the direction where the azimuth equals
//0 degrees. To do so, switch the 0 below with 180.  
float northOrSouth = 180;
float pi = 3.14159265;

//Seguidor
// Variables seguidor
int x0;
int x1;
int x2;
int x3;
int x;
int y0;
int y1;
int y2;
int y3;
int y;
float hor;
float ver; 
float hor0;
float ver0; 

unsigned long tiempo;
int amp=2;
bool convergencia = true;


void wakeUpNow()        // here the interrupt is handled after wakeup
{
  // execute code here after wake-up before returning to the loop() function
  // timers and code using timers (serial.print and more...) will not work here.
  // we don't really need to execute any special functions here, since we
  // just want the thing to wake up
}

void setup()
{
  // put your setup code here, to run once:
  pinMode(wakePin, INPUT);
  Wire.begin();

  A1Day = byte(14);
  A1Hour = byte(0);
  A1Minute = byte(55);  // si coloca 0 la alarma se activara en 10, si no entiende lea la biblia
  A1Second = byte(0);
  AlarmBits = B11100;
  A1Dy = false;
  A1h12 = false;
  A1PM = false;
 
  Serial.begin(115200);
  Clock.setA1Time(A1Day, A1Hour, A1Minute, A1Second, AlarmBits, A1Dy, A1h12, A1PM);
  Clock.turnOnAlarm(1);
  
  //codigo mágico que pone en high la alarma
  //Revision precencia de alarma
  Clock.checkIfAlarm(1);
  delay(1000);
  /* Now it is time to enable an interrupt. In the function call
     attachInterrupt(A, B, C)
     A   can be either 0 or 1 for interrupts on pin 2 or 3.

     B   Name of a function you want to execute while in interrupt A.

     C   Trigger mode of the interrupt pin. can be:
                 LOW        a low level trigger
                 CHANGE     a change in level trigger
                 RISING     a rising edge of a level trigger
                 FALLING    a falling edge of a level trigger

     In all but the IDLE sleep modes only LOW can be used.
  */

  attachInterrupt(1, wakeUpNow, LOW); // use interrupt 1 (pin 3) and run function
  // wakeUpNow when pin 3 gets LOW
}

void sleepNow()         // here we put the arduino to sleep
{
  /* Now is the time to set the sleep mode. In the Atmega8 datasheet
     http://www.atmel.com/dyn/resources/prod_documents/doc2486.pdf on page 35
     there is a list of sleep modes which explains which clocks and
     wake up sources are available in which sleep mode.

     In the avr/sleep.h file, the call names of these sleep modes are to be found:

     The 5 different modes are:
         SLEEP_MODE_IDLE         -the least power savings
         SLEEP_MODE_ADC
         SLEEP_MODE_PWR_SAVE
         SLEEP_MODE_STANDBY
         SLEEP_MODE_PWR_DOWN     -the most power savings

     For now, we want as much power savings as possible, so we
     choose the according
     sleep mode: SLEEP_MODE_PWR_DOWN

  */
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);   // sleep mode is set here

  sleep_enable();          // enables the sleep bit in the mcucr register
  // so sleep is possible. just a safety pin

  /* Now it is time to enable an interrupt. We do it here so an
     accidentally pushed interrupt button doesn't interrupt
     our running program. if you want to be able to run
     interrupt code besides the sleep function, place it in
     setup() for example.

     In the function call attachInterrupt(A, B, C)
     A   can be either 0 or 1 for interrupts on pin 2 or 3.

     B   Name of a function you want to execute at interrupt for A.

     C   Trigger mode of the interrupt pin. can be:
                 LOW        a low level triggers
                 CHANGE     a change in level triggers
                 RISING     a rising edge of a level triggers
                 FALLING    a falling edge of a level triggers

     In all but the IDLE sleep modes only LOW can be used.
  */

  attachInterrupt(1, wakeUpNow, LOW); // use interrupt 1 (pin 3) and run function
  // wakeUpNow when pin 3 gets LOW

  sleep_mode();            // here the device is actually put to sleep!!
  // THE PROGRAM CONTINUES FROM HERE AFTER WAKING UP

  sleep_disable();         // first thing after waking from sleep:
  // disable sleep...
  detachInterrupt(1);      // disables interrupt 1 on pin 3 so the
  // wakeUpNow code will not be executed
  // during normal running time.
}

void loop()
{
  float delta;
  float h;
  float altitude;
  float azimuth;
  float correctaz;
  float correctal;
  int factor_s = 1;

  //////////////////////////////////////////////////  
  //PUT YOUR LATITUDE, LONGITUDE, AND TIME ZONE HERE
  // TUPPER 2007
  float latitude = -33.458017;
  float longitude = -70.661989;
  // ROSSINI 10620
  //float latitude = -33.5622523;
  //float longitude = -70.603821799;
  //float timezone = 0;
  // Valle Nevado
  //float latitude = -33.44888969;
  //float longitude = -70.6692655;
  float timezone = 0;

  //////////////////////////////////////////////////  
  //codigo mágico que pone en high la alarma
  //Revision precencia de alarma
  Clock.checkIfAlarm(1);
  delay(1000);

  //  Obtención del tiempo
  Clock.getA1Time(ADay, AHour, AMinute, ASecond, ABits, ADy, A12h, Apm);  
  
  second = Clock.getSecond();
  minute = Clock.getMinute();
  hour = Clock.getHour(h12, PM);
  day = Clock.getDate();
  month = Clock.getMonth(Century);
  year = Clock.getYear();

  Serial.print("20");
  Serial.print(int(year), DEC);
  Serial.print('-');
  Serial.print(int(month), DEC);
  Serial.print('-');
  Serial.print(int(day), DEC);
  Serial.print(' ');
  Serial.print(int(hour), DEC);
  Serial.print(':');
  Serial.print(int(minute), DEC);
  Serial.print(':');
  Serial.println(int(second), DEC);
  delay(100);

//START OF THE CODE THAT CALCULATES THE POSITION OF THE SUN
  latitude = latitude * pi/180;
  float n = daynum(month) + day;//NUMBER OF DAYS SINCE THE START OF THE YEAR. 
  delta = .409279 * sin(2 * pi * ((284 + n)/365.25));//SUN'S DECLINATION.
  day = dayToArrayNum(day);//TAKES THE CURRENT DAY OF THE MONTH AND CHANGES IT TO A LOOK UP VALUE ON THE HOUR ANGLE TABLE.
  h = (FindH(day,month)) + longitude + (timezone * -1 * 15);//FINDS THE NOON HOUR ANGLE ON THE TABLE AND MODIFIES IT FOR THE USER'S OWN LOCATION AND TIME ZONE.
  h = ((((hour + minute/60) - 12) * 15) + h)*pi/180;//FURTHER MODIFIES THE NOON HOUR ANGLE OF THE CURRENT DAY AND TURNS IT INTO THE HOUR ANGLE FOR THE CURRENT HOUR AND MINUTE.
  altitude = (asin(sin(latitude) * sin(delta) + cos(latitude) * cos(delta) * cos(h)))*180/pi;//FINDS THE SUN'S ALTITUDE.
  azimuth = ((atan2((sin(h)),((cos(h) * sin(latitude)) - tan(delta) * cos(latitude)))) + (northOrSouth*pi/180)) *180/pi;//FINDS THE SUN'S AZIMUTH.
  
  //END OF THE CODE THAT CALCULATES THE POSITION OF THE SUN
  Serial.println(azimuth);
  Serial.println(altitude);
  
  if ((azimuth >= 0) and (azimuth <= 90))
  {
    correctaz = (90-azimuth);
    correctal = (altitude-90);

  }
  else if ((azimuth > 90) and (azimuth <= 180))
  {
    correctaz = (90-azimuth);
    correctal = (altitude-90);
  }
    else if ((azimuth > 180) and (azimuth < 270))
  {
    correctaz = (270-azimuth);
    correctal = (90-altitude);
    factor_s = -1;
  }
  else
  {
    correctaz = (270-azimuth);
    correctal = 90-altitude;
    factor_s = -1;
  }

  Serial.println(correctaz);
  Serial.println(correctal);
  
  hor = correctaz;
  ver = correctal;
  hor0 = correctaz;
  ver0 = correctal;
  delay(100);

  // Programacion proximo reinicio
  A1Minute = A1Minute + byte(5);
  if (A1Minute >= byte(60))
  {
    A1Minute = A1Minute - byte(60);
  }
  
  delay(100);
  Serial.println(A1Minute);
  delay(100);
  Serial.println("Proximo despertar en 10 minutos");
  delay(100);

  // Seteo de la alarma próximo reinicio
  Clock.setA1Time(A1Day, A1Hour, A1Minute, A1Second, AlarmBits, A1Dy, A1h12, A1PM);
  //Clock.turnOffAlarm(1);
  //Clock.turnOnAlarm(1);
  Serial.println("Alarma activada");
  delay(100);
//********************************************************************************************************************************************
//CODIGO DEL SEGUIDOR AQUI
//********************************************************************************************************************************************
  // Iniciamos las conexiones de energia a los motores, arduino uno y shield M2M
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(13, OUTPUT);
  
  //Pin de conexion con arduino uno
  pinMode(2, OUTPUT);

  if (altitude >= 7)
  {
  digitalWrite(4, HIGH); // Desconexion Motores
  digitalWrite(5, HIGH); // Motor 1
  digitalWrite(6, HIGH); // Motor 2

  Herkulex.begin(57600,10,9); //open serial with rx=10 and tx=11
  Herkulex.reboot(0); //reboot first motor
  Herkulex.reboot(1); //reboot second motor
  delay(500); 
  Herkulex.initialize(); //initialize motors

  Herkulex.moveOneAngle(0, 160, 0,2); //move to position 200 in 1500 milliseconds
  Herkulex.moveOneAngle(1, 00, 0,2); //move to 820 position in 500 milliseconds
  delay(500);
  Herkulex.moveOneAngle(0, correctal, 1000,2); //move to position 200 in 1500 milliseconds
  Herkulex.moveOneAngle(1, correctaz, 1000,2); //move to 820 position in 500 milliseconds
  delay(1000);
  
  digitalWrite(7, HIGH); // Desconexion arduino UNO y M2M
  digitalWrite(8, HIGH); //Arduino UNO
  digitalWrite(13,HIGH); // M2M shield
  
  //Serial.begin(115200);
  
  x0 = 1; // Inicializamos el elemento derivativo
  y0 = 1;
  tiempo = millis();
  
  int a = 6;
  bool test_found = false;

    convergencia = true;
    Serial.println(millis());
    Serial.println(tiempo+130000); 
    while(millis() < tiempo + 130000)
    {
      // Lectura de los sensores:
      int sensor0 = analogRead(A0);
      delay(1);
      int sensor1 = analogRead(A1);
      delay(1);
      int sensor2 = analogRead(A2);
      delay(1);
      int sensor3 = analogRead(A3);
      delay(1);
      
      int suma = sensor0 + sensor1 + sensor2 + sensor3;
      int comb01 = sensor0 + sensor1;
      int comb32 = sensor3 + sensor2;
      int comb03 = sensor0 + sensor3;
      int comb12 = sensor1 + sensor2;

      // Comparamos entradas opuesta y desacoplamos las respuestas
      if (sensor0 >= sensor2)
      {
        x1 = factor_s*-1;
        y1 = 1;
      }
      else
      {
        x1 = factor_s*1;
        y1 = -1;
      }

      if (sensor1 >= sensor3)
      {
        x2 = factor_s*1;
        y2 = 1;
      }
      else
      {
        x2 = factor_s*-1;
        y2 = 1;
      }

      if (comb01 >= comb32)
      {
         y3 = 1;
      }
      else
      {
        y3 = -1;
      }

      
      if (comb03 >= comb12)
      {
        x3 = factor_s*-1;
      }
      else
      {
        x3 = factor_s*1;
      }

      x = x1 + x2 + x3;
      y = y1 + y2 + y3;
      
  //Agregamos el elemento integral para evitar el error en estado estaiconario
     
      if (x == 0)
      {
        x = x0;  
      }
      else
      {
        x0 = x; 
      }
  
      if (y == 0)
      {
        y = y0;
      }
      else
      {
        y0 = y;
      }
      
// Eliminamos cuando el valor es de 2
      x = x/abs(x);
      y = y/abs(y);

      hor0 = hor0 + 0.3*x;
      ver0 = ver0 + 0.3*y;
      
      if ((hor0 > hor+30) or (hor0 < hor-30) )
      {
        hor0 = hor;
      }
    
      if ((ver0 > ver+30) or (ver0 < ver-30) )
      {
        ver0 = ver;
      }

      if (suma >= 0)
      //if (suma >= 200)
      {
        amp = 1;
        if (convergencia)
        {
          //señal arduino uno de medir A ESTA PARTE NO ACCEDE CUANDO SE HACEN PRUEBAS DE LABORATORIO
          digitalWrite(2, HIGH); 
          convergencia = false; 
        } 
      }
      else
      {
        amp = 2;
      }
      //Ejecutamos el seguimiento
      Herkulex.moveOneAngle(0, ver0, 0,2); 
      Herkulex.moveOneAngle(1, hor0, 0,2); 
    }
  

  // Ramp-down
  Herkulex.moveOneAngle(0, 160, 1000,2); 
  Herkulex.moveOneAngle(1, 00, 1000,2); 
  delay(2000);
  Herkulex.end();
  delay(1000);
  // Apagamos la energia de los motores
  digitalWrite(4, LOW);
  
  //informamos al arduino UNO que termina la medición
  digitalWrite(2,LOW);
  //delay(100);
  //pinMode(2,INPUT);
  delay(110000);
  digitalWrite(7, LOW);
  }
  Serial.println("OK");
  delay(1000);
  //Apagamos arduino Uno y M2M
//********************************************************************************************************************************************
//FIN CODIGO
//********************************************************************************************************************************************
  sleepNow();     // sleep function called here

}

bool found(int sensor0, int sensor1, int sensor2, int sensor3)
{
      // Comparamos entradas opuesta y desacoplamos las respuestas
      // Basta que se cumpla una condición para que se justifique
      // Se usa para la busqueda aproximada del sol
      if (abs(sensor0-sensor2)>=4)
      {
        return true;
      }

      else if (abs(sensor1-sensor3)>=4)
      {
        return true;
      }
      else
      {
        return false;
      }
}
