#include <Wire.h>
#include "FastLED.h"

#define DEBUG 0
#if DEBUG == 1
#define DBG(x) x
#else
#define DBG(x)
#endif

// How many leds in your strip?
#define NUM_LEDS 12
// Is your strip upside down?
#define REVERSE 1
#define MOD (REVERSE ? NUM_LEDS/2 : 0)

// For led chips like Neopixels, which have a data line, ground, and power, you just
// need to define DATA_PIN.  For led chipsets that are SPI based (four wires - data, clock,
// ground, and power), like the LPD8806 define both DATA_PIN and CLOCK_PIN
#define DATA_PIN1 9
#define DATA_PIN2 8
#define DATA_PIN3 7

#define COLOR_ON_1 CRGB( 32, 0, 32)
#define COLOR_ON_2 CRGB( 32, 16, 0)
#define COLOR_ON_3 CRGB( 0, 32, 0)
#define COLOR_OFF  CRGB::Black

// Define the array of leds
CRGB leds1[NUM_LEDS];
CRGB leds2[NUM_LEDS];
CRGB leds3[NUM_LEDS];

void setup() {
  FastLED.addLeds<NEOPIXEL, DATA_PIN1>(leds1, NUM_LEDS);
  FastLED.addLeds<NEOPIXEL, DATA_PIN2>(leds2, NUM_LEDS);
  FastLED.addLeds<NEOPIXEL, DATA_PIN3>(leds3, NUM_LEDS);

  // Turn the LED on, then pause
  for (int i = 0; i < NUM_LEDS; i++) {
    leds1[i] = COLOR_ON_1;
    leds2[i] = COLOR_ON_2;
    leds3[i] = COLOR_ON_3;
    FastLED.show();
    delay(100);
  }

  // Now turn the LED off, then pause
  for (int i = 0; i < NUM_LEDS; i++) {
    leds1[i] = COLOR_OFF;
    leds2[i] = COLOR_OFF;
    leds3[i] = COLOR_OFF;
    FastLED.show();
    delay(100);
  }

  Wire.begin(0x2D);             // join i2c bus with address #8
  Wire.onReceive(receiveEvent); // register event
  DBG(Serial.begin(9600);)      // start serial for output
}

void loop() {
  delay(100);
}

void receiveEvent(int bytes) {
  DBG(Serial.println(bytes);)
  unsigned int i  = 0;
  char m[4] = {0, 0, 0, 0};

  if(Wire.read() == 0x20) {
    for(i = 0; i < sizeof(m); i++) {
      m[i] = Wire.read();
    }

    while(Wire.available()) Wire.read();

    DBG(Serial.println("====");)
    DBG(Serial.println(m[0]);)
    DBG(Serial.println(m[1]);)
    DBG(Serial.println(m[2]);)
    DBG(Serial.println("====");)
  
    if(m[3] == '\n') {
      DBG(Serial.println("Opening leds");)
      for(int i = 0; i < NUM_LEDS; i++) {
        int j = (i < NUM_LEDS/2) ? (i + MOD) : (i - MOD);
        leds1[j] = (i < m[0] - (m[0] < 'A' ? '0' : (m[0] < 'a' ? 'A' - 10 : 'a' - 10))) ? COLOR_ON_1 : COLOR_OFF;
        leds2[j] = (i < m[1] - (m[1] < 'A' ? '0' : (m[1] < 'a' ? 'A' - 10 : 'a' - 10))) ? COLOR_ON_2 : COLOR_OFF;
        leds3[j] = (i < m[2] - (m[2] < 'A' ? '0' : (m[2] < 'a' ? 'A' - 10 : 'a' - 10))) ? COLOR_ON_3 : COLOR_OFF;
      }
      FastLED.show();
    }
  } else while(Wire.available()) Wire.read();
}
