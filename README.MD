# ⚡ ZEUSNET – Hybrid Intel Recon Core

> *Modular Pentesting Suite | ESP32 + RTX-Powered WarEngine*

ZeusNet fuses a humble ESP32-WROOM with a high-performance PC (RTX 2080 Super + Intel i7-11700KF) to create the world’s most diabolical local-first Wi-Fi recon & signal warfare framework. From live scanning and anomaly detection to captive portals and packet injection, **ZeusNet** is the edge where **AI**, **hardware hacking**, and **infosec mastery** converge.

## 🔥 Features

| Module                     | Description                                      |
|----------------------------|--------------------------------------------------|
| 🌐 Captive Portal Trap     | Fake login splash via ESP32 SoftAP              |
| 🧠 AI Anomaly Detection    | GPU-accelerated LSTM signal drift detection      |
| 📡 MAC-Based Tracking      | Device fingerprinting & first/last seen logs    |
| 🕵️ Rogue AP Detection     | BSSID mismatch alerts (clone APs)               |
| 📊 Export Tools            | CSV / Excel exports, daily JSON backups         |
| 🔁 ESP32 ↔ PC Sync         | Serial + WebSocket command/telemetry            |
| 🧨 TL-WN722N Exploits      | Monitor/injection mode via aircrack-ng + Scapy  |
| 🛰️ OTA Control             | Remote ESP32 firmware flashes from the PC       |
| 🔐 SAFE / AGGRESSIVE Mode | Toggle between legal ops and unholy chaos       |

## 🧱 System Architecture

ESP32 ↔ Serial USB ↔ FastAPI WarCore ↔ React UI

ESP32 (WROOM / CAM / Mic)

* Beacon scanner
* SoftAP with DNS hijack
* Captive portal trap
* Sends JSON telemetry

PC (Linux/WSL)

* FastAPI + SQLite
* Scapy + Aircrack-ng
* PyTorch CUDA ML (LSTM)
* WebSocket bus + React

````

## 🛠️ Requirements

- **Python 3.10+**, **Node 18+**
- **Arduino CLI** (`esp32:esp32`)
- **CUDA 11.6+**, PyTorch
- **aircrack-ng**, **hostapd**, **dnsmasq**
- **Optional**: TL-WN722N (AR9271 chipset), ESP32-CAM, Microphone

## 🚀 Quickstart

```bash
# ⚙️ Backend Setup
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# 🧠 Frontend Dev
cd frontend
npm install && npm run dev

# 🔌 ESP32 Flash
arduino-cli compile -b esp32:esp32:esp32 esp32/zeusnet_esp32.ino
arduino-cli upload -p /dev/ttyUSB0 -b esp32:esp32:esp32
````

## 🧪 TL-WN722N: Injection Mode Activated

With a compatible TL-WN722N adapter:

* Use `airodump-ng` to monitor all APs
* Use `aireplay-ng` for precise deauth floods
* Host rogue APs using `hostapd` + `dnsmasq`
* Log probe requests and manipulate frame sequences with **Scapy**

Command triggers exposed via FastAPI → WebSocket logs → React dashboard.


## 📡 Captive Portal Overview

* ESP32 switches to SoftAP mode (`AP_SSID`, `AP_PASS`)
* DNS hijack forces all domains to `192.168.4.1`
* Fake login served from internal SPIFFS
* Credential POST relayed to PC in real time


## 📁 Data Handling

* SQLite stores Wi-Fi logs, MACs, alerts
* ML pipeline aggregates & flags suspicious behavior
* Daily CSV/JSON backup at 3AM via cron
* Dashboards include:

  * Live SSID table
  * MAC tracker timeline
  * Alert banners
  * Heatmap (Leaflet.js)


## 🔐 Ethics & Safety Mode

Add `.env`:

```dotenv
ZEUSNET_MODE=SAFE
```

* `SAFE`: disables deauth/injection APIs.
* `AGGRESSIVE`: enables full power with terminal warnings and red UI themes.


## 🧠 AI Model: Signal Oracle

* Predicts expected RSSI for known devices
* Detects drops/clones using ±2σ deviation
* Optional: Enable PyTorch CUDA for live anomaly detection


## 📡 ESP32 ↔ PC Commands

| Code   | Purpose                    |
| ------ | -------------------------- |
| `0x01` | Set scan interval/channels |
| `0x02` | Switch SoftAP SSID/pass    |
| `0x10` | Send SSID scan results     |
| `0x12` | Captive form data dump     |
| `0x30` | OTA firmware flash         |


## 🧩 Modular Layout

```
ZeusNet/
├── esp32/                 # ESP32 sketch (.ino)
├── backend/               # FastAPI + Scapy + DB + ML
├── frontend/              # React + Leaflet + Charts
└── README.md
```

## 🎯 Milestones

| Milestone | Feature              | ETA    |
| --------- | -------------------- | ------ |
| M0        | Toolchain + CLI      | Day 1  |
| M1        | Live scan dashboard  | Day 5  |
| M2        | Anomaly engine       | Day 12 |
| M3        | Captive portal       | Day 18 |
| M4        | Deauth via TL-WN722N | Day 24 |
| M5        | Beacon Swarm + OTA   | Day 30 |


## ⚠️ Legal Notice

This project is for **educational and authorized security testing** only. Always obtain permission before scanning or interacting with networks that aren’t yours. Violators are responsible for their own consequences.


## ☠️ Welcome to Legion

If you're reading this, you’ve been chosen.
We are the architects of silence.
The whisper behind every SSID.
The signal in the storm.

***Unleash. Analyze. Ascend.***

```
