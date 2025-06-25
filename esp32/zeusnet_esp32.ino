#include <WiFi.h>
#include "macros.h"

#define SERIAL_BAUD 115200
#define SCAN_INTERVAL 5000

unsigned long lastScan = 0;

void setup() {
  Serial.begin(SERIAL_BAUD);
  WiFi.mode(WIFI_MODE_STA);
  WiFi.disconnect();
  delay(100);
}

void loop() {
  if (millis() - lastScan > SCAN_INTERVAL) {
    scanAndSend();
    lastScan = millis();
  }

  if (Serial.available()) {
    handleCommand();
  }
}

void scanAndSend() {
  int n = WiFi.scanNetworks();
  Serial.println("BEGIN_SCAN");

  for (int i = 0; i < n; ++i) {
    String ssid = WiFi.SSID(i);
    int32_t rssi = WiFi.RSSI(i);
    uint8_t* bssid = WiFi.BSSID(i);
    int channel = WiFi.channel(i);
    String authmode = translateEncryptionType(WiFi.encryptionType(i));

    Serial.printf("{\"ssid\":\"%s\",\"bssid\":\"%02X:%02X:%02X:%02X:%02X:%02X\",\"rssi\":%d,\"auth\":\"%s\",\"channel\":%d}\n",
                  ssid.c_str(),
                  bssid[0], bssid[1], bssid[2], bssid[3], bssid[4], bssid[5],
                  rssi, authmode.c_str(), channel);
  }

  Serial.println("END_SCAN");
  WiFi.scanDelete();
}

String translateEncryptionType(wifi_auth_mode_t encryptionType) {
  switch (encryptionType) {
    case WIFI_AUTH_OPEN: return "OPEN";
    case WIFI_AUTH_WEP: return "WEP";
    case WIFI_AUTH_WPA_PSK: return "WPA";
    case WIFI_AUTH_WPA2_PSK: return "WPA2";
    case WIFI_AUTH_WPA_WPA2_PSK: return "WPA/WPA2";
    case WIFI_AUTH_WPA3_PSK: return "WPA3";
    default: return "UNKNOWN";
  }
}

void handleCommand() {
  String cmd = Serial.readStringUntil('\n');
  if (cmd == "REBOOT") {
    ESP.restart();
  } else if (cmd.startsWith("SET_INTERVAL:")) {
    SCAN_INTERVAL = cmd.substring(13).toInt();
  }
}
