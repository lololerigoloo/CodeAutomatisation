#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>
#define TFT_CS   10
#define TFT_DC   9
#define TFT_RST  8

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

void setup() {
  tft.init(240, 320);
  tft.setRotation(1);
  tft.fillScreen(ST77XX_BLACK);
  tft.setCursor(10, 10);
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(5);
  tft.println("Nigger");
}

void loop() {
  int16_t x = 10;
  int16_t y = 10;
  while(true){
    x += 10;
    y +=5;
    tft.setCursor(((x) %240) , ((y)%320));
    tft.fillScreen(ST77XX_BLACK);
    tft.println("Nigger");
    delay(100);
  }
}