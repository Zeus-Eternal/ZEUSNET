#include <WiFi.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include "macros.h"

#define SERIAL_BAUD 115200

struct Config {
  uint32_t interval = 5000;   // scan delay in ms
  uint8_t channel = 1;        // WiFi channel (unused for now)
  bool scanning = true;       // enable/disable scanning
} cfg;

unsigned long lastScan = 0;
Preferences prefs;

void loadConfig() {
  prefs.begin("zeusnet", false);
  cfg.interval = prefs.getULong("interval", 5000);
  cfg.channel = prefs.getUChar("channel", 1);
  cfg.scanning = prefs.getBool("scanning", true);
  prefs.end();
}

void saveConfig() {
  prefs.begin("zeusnet", false);
  prefs.putULong("interval", cfg.interval);
  prefs.putUChar("channel", cfg.channel);
  prefs.putBool("scanning", cfg.scanning);
  prefs.end();
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  loadConfig();
  WiFi.mode(WIFI_MODE_STA);
  WiFi.disconnect();
  delay(100);
}

void loop() {
  if (cfg.scanning && millis() - lastScan > cfg.interval) {
    scanAndSend();
    lastScan = millis();
  }

  if (Serial.available()) {
    handleCommand();
  }
}

void scanAndSend() {
  int n = WiFi.scanNetworks();
  for (int i = 0; i < n; ++i) {
    String ssid = WiFi.SSID(i);
    int32_t rssi = WiFi.RSSI(i);
    uint8_t* bssid = WiFi.BSSID(i);
    int channel = WiFi.channel(i);
    String authmode = translateEncryptionType(WiFi.encryptionType(i));

    char macbuf[18];
    sprintf(macbuf, "%02X:%02X:%02X:%02X:%02X:%02X", bssid[0], bssid[1], bssid[2], bssid[3], bssid[4], bssid[5]);

    StaticJsonDocument<192> doc;
    doc["opcode"] = OPCODE_SCAN_RESULT;
    JsonObject pl = doc.createNestedObject("payload");
    pl["ssid"] = ssid;
    pl["bssid"] = macbuf;
    pl["rssi"] = rssi;
    pl["auth"] = authmode;
    pl["channel"] = channel;

    serializeJson(doc, Serial);
    Serial.println();
  }

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
  String line = Serial.readStringUntil('\n');
  StaticJsonDocument<128> doc;
  DeserializationError err = deserializeJson(doc, line);
  if (err) {
    return;  // Ignore malformed
  }
  int opcode = doc["opcode"] | 0;
  JsonVariant payload = doc["payload"];

  if (opcode == OPCODE_REBOOT) {
    ESP.restart();
  } else if (opcode == OPCODE_CONFIG && payload.is<JsonObject>()) {
    if (payload.containsKey("interval")) {
      cfg.interval = payload["interval"].as<uint32_t>();
    }
    if (payload.containsKey("channel")) {
      cfg.channel = payload["channel"].as<uint8_t>();
    }
    if (payload.containsKey("scanning")) {
      cfg.scanning = payload["scanning"].as<bool>();
    }
    saveConfig();
    StaticJsonDocument<64> ack;
    ack["opcode"] = OPCODE_CONFIG;
    ack["status"] = "ok";
    serializeJson(ack, Serial);
    Serial.println();
  }
}
