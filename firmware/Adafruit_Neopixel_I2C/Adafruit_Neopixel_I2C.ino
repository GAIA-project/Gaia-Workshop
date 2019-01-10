#include <Wire.h>
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
#define DATA_PIN1 7
#define DATA_PIN2 8
#define DATA_PIN3 9

#define BRIGHTNESS 50

Adafruit_NeoPixel strip1 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN1, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN2, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip3 = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN3, NEO_GRBW + NEO_KHZ800);

uint32_t c1 = Adafruit_NeoPixel::Color(32, 0, 32);
uint32_t c2 = Adafruit_NeoPixel::Color(32, 16, 0);
uint32_t c3 = Adafruit_NeoPixel::Color(0, 32, 0);
uint32_t c0 = Adafruit_NeoPixel::Color(0, 0, 0);

uint32_t leds1[NUM_LEDS];
uint32_t leds2[NUM_LEDS];
uint32_t leds3[NUM_LEDS];

void setup() {

  Wire.begin(0x2D);             // join i2c bus with address #8
  Wire.onReceive(receiveEvent); // register event
  //Serial.begin(9600);           // start serial for output

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
  delay(100);
}

void setStripColor(Adafruit_NeoPixel* strip, uint32_t* leds) {
  for (int i = 0; i < NUM_LEDS; i++) {
    strip->setPixelColor(i, leds[i]);
    strip->show();
  }
}

void receiveEvent(int bytes) {
  //Serial.println(bytes);
  unsigned int i  = 0;
  char m[4] = {0, 0, 0, 0};

  if(Wire.read() == 0x20){
    for(i = 0; i < sizeof(m); i++) {
      m[i] = Wire.read();
    }

    //Serial.println("====");
    //Serial.println(m[0]);
    //Serial.println(m[1]);
    //Serial.println(m[2]);
    //Serial.println("====");
  
    if(m[3] == '\n') {
      //Serial.println("Opening leds");
      for (int i = 0; i < NUM_LEDS; i++) {
        int j = (i < NUM_LEDS/2) ? (i + MOD) : (i - MOD);
        leds1[j] = (i < m[0] - (m[0] < 'A' ? '0' : (m[0] < 'a' ? 'A' - 10 : 'a' - 10))) ? c1 : c0;
        leds2[j] = (i < m[1] - (m[1] < 'A' ? '0' : (m[1] < 'a' ? 'A' - 10 : 'a' - 10))) ? c2 : c0;
        leds3[j] = (i < m[2] - (m[2] < 'A' ? '0' : (m[2] < 'a' ? 'A' - 10 : 'a' - 10))) ? c3 : c0;
      }
      setStripColor(&strip1, leds1);
      setStripColor(&strip2, leds2);
      setStripColor(&strip3, leds3);
    }
  }
}
