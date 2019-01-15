#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

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
#define DATA_PIN1 7
#define DATA_PIN2 8
#define DATA_PIN3 9

#define COLOR_ON_1 Adafruit_NeoPixel::Color(32, 0, 32)
#define COLOR_ON_2 Adafruit_NeoPixel::Color(32, 16, 0)
#define COLOR_ON_3 Adafruit_NeoPixel::Color(0, 32, 0)
#define COLOR_OFF  Adafruit_NeoPixel::Color(0, 0, 0)

#define BRIGHTNESS 50
Adafruit_NeoPixel strip1 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN1, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN2, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip3 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN3, NEO_GRBW + NEO_KHZ800);

void setup() {
  strip1.setBrightness(BRIGHTNESS);
  strip1.begin();
  strip1.show(); // Initialize all pixels to 'off'

  strip2.setBrightness(BRIGHTNESS);
  strip2.begin();
  strip2.show(); // Initialize all pixels to 'off'

  strip3.setBrightness(BRIGHTNESS);
  strip3.begin();
  strip3.show(); // Initialize all pixels to 'off'

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
        strip1.setPixelColor(j, (i < m[0] - (m[0] < 'A' ? '0' : (m[0] < 'a' ? 'A' - 10 : 'a' - 10))) ? COLOR_ON_1 : COLOR_OFF);
        strip2.setPixelColor(j, (i < m[1] - (m[1] < 'A' ? '0' : (m[1] < 'a' ? 'A' - 10 : 'a' - 10))) ? COLOR_ON_2 : COLOR_OFF);
        strip3.setPixelColor(j, (i < m[2] - (m[2] < 'A' ? '0' : (m[2] < 'a' ? 'A' - 10 : 'a' - 10))) ? COLOR_ON_3 : COLOR_OFF);
      }
      strip1.show();
      strip2.show();
      strip3.show();
    }
  } else while(Wire.available()) Wire.read();
}
