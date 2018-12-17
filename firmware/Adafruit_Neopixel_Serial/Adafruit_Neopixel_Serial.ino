#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

// How many leds in your strip?
#define NUM_LEDS 12
// Is your strip upside down?
#define REVERSE 1
#define MOD (REVERSE ? NUM_LEDS/2 : 0)

// For led chips like Neopixels, which have a data line, ground, and power, you just
// need to define DATA_PIN.  For led chipsets that are SPI based (four wires - data, clock,
// ground, and power), like the LPD8806 define both DATA_PIN and CLOCK_PIN
#define DATA_PIN1 2
#define DATA_PIN2 3
#define DATA_PIN3 4

#define BRIGHTNESS 50

Adafruit_NeoPixel strip1 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN1, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN2, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip3 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN3, NEO_GRBW + NEO_KHZ800);


uint32_t c1=strip1.Color(32, 0, 32);
uint32_t c2=strip2.Color(32, 16, 0);
uint32_t c3=strip3.Color(0, 32, 0);
uint32_t c0=strip3.Color(0, 0, 0);

bool leds1 [NUM_LEDS];
bool leds2 [NUM_LEDS];
bool leds3 [NUM_LEDS];

void setup() {

  Serial.begin(9600);
  // while the serial stream is not open, do nothing:
  while (!Serial) ;

    // This is for Trinket 5V 16MHz, you can remove these three lines if you are not using a Trinket
  #if defined (__AVR_ATtiny85__)
    if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
  #endif
  // End of trinket special code
  strip1.setBrightness(BRIGHTNESS);
  strip1.begin();
  strip1.show(); // Initialize all pixels to 'off'

  strip2.setBrightness(BRIGHTNESS);
  strip2.begin();
  strip2.show(); // Initialize all pixels to 'off'

  strip3.setBrightness(BRIGHTNESS);
  strip3.begin();
  strip3.show(); // Initialize all pixels to 'off'

}

void loop() {

  if (Serial.available() > 0 ) {
    Serial.println( Serial.available() );

    char m[3] = {0, 0, 0};
    Serial.readBytes(m, 3);

    Serial.println("====");
    Serial.println(m[0]);
    Serial.println(m[1]);
    Serial.println(m[2]);
    Serial.println("====");
    strip1.setPixelColor(1, c1);
    strip1.show();
    for (int i = 0; i < NUM_LEDS; i++) {
        int j = (i < NUM_LEDS/2) ? (i + MOD) : (i - MOD);
        leds1[j] = (i < m[0] - (m[0] < 'A' ? '0' : (m[0] < 'a' ? 'A' - 10 : 'a' - 10))) ? 1 : 0;
        leds2[j] = (i < m[1] - (m[1] < 'A' ? '0' : (m[1] < 'a' ? 'A' - 10 : 'a' - 10))) ? 1 : 0;
        leds3[j] = (i < m[2] - (m[2] < 'A' ? '0' : (m[2] < 'a' ? 'A' - 10 : 'a' - 10))) ? 1 : 0;
     }
    if (Serial.read() == '\n') {
      for (int i = 0; i < NUM_LEDS; i++) {
          if (leds1[i]==1)
           {
                  strip1.setPixelColor(i, c1);
                  strip1.show();
                 //  delay(50);
           }
          else
          {
                 strip1.setPixelColor(i, c0);
                  strip1.show();
                  // delay(50);
          }
       }
       for (int i = 0; i < NUM_LEDS; i++) {
          if (leds2[i]==1)
           {
                  strip2.setPixelColor(i, c2);
                  strip2.show();
                 //  delay(50);
           }
          else
          {
                 strip2.setPixelColor(i, c0);
                 strip2.show();
                  // delay(50);
          }
       }
       for (int i = 0; i < NUM_LEDS; i++) {
          if (leds3[i]==1)
           {
                  strip3.setPixelColor(i, c1);
                  strip3.show();
                 //  delay(50);
           }
          else
          {
                 strip3.setPixelColor(i, c0);
                 strip3.show();
                  // delay(50);
          }
      }
    }
  }
}

