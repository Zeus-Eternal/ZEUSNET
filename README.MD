# ⚡ ZEUSNET – Hybrid Esp32 + PC Tactical Recon Platform

> *“Not all war is visible. Some of it floats in signals and shadows.”*

**ZeusNet** turns an ESP32-WROOM module and a high-powered PC into a modular **Wi-Fi pentesting + recon AI node**. A Wi-Fi scanner on the surface. A command & control system beneath. Designed to observe, learn, deceive—and dominate.

## 🚀 Features

| Phase | Feature                      | Description                                         |
|-------|------------------------------|-----------------------------------------------------|
| 1     | 📡 Wi-Fi Scanner             | Real-time SSID/RSSI capture from ESP32             |
| 1     | 📊 React Dashboards          | Signal strength graphs, channel heatmaps           |
| 2     | 🌐 Captive Portal Trap       | ESP32 SoftAP with DNS hijack and spoofed login     |
| 2     | 🧠 AI Anomaly Detection      | ML detects rogue APs, signal drops, and MAC spikes |
| 2     | 📁 Auto Backup System        | Daily JSON/CSV dumps to `/backups`                 |
| 2     | 📡 MAC Tracker               | First/last-seen detection with device heatmaps     |
| 3     | 👻 Beacon Swarm (Mirage)     | ESP32 beacon flood for network noise               |
| 3     | 🔥 Deauth & Injection (Obsidian Jammer) | TL-WN722N powered—advanced signal disruption |
| 3     | 🧬 GPU Pattern Oracle        | LSTM anomaly detection using RTX CUDA power        |
| 3     | 🛰 OTA Fleet Control         | OTA flash updates to ESP32 via command bus         |
| 3     | 🕵️ Rogue AP Detection       | SSID/BSSID mismatches across zones                 |

## 🛠 Hardware Required

- **ESP32-WROOM** (primary node)
- **TL-WN722N (AR9271)** USB Wi-Fi Adapter
- PC with:
  - CPU: Intel i7-11700KF
  - GPU: RTX 2080 Super
  - RAM: 32GB
- Optional: ESP32-CAM, mic sensor, GPS for field deployments

## 🧱 Folder Structure

```plaintext
ZeusNet/
├── esp32/                # ESP32 firmware: scanning, portals
├── backend/              # FastAPI + AI command core
├── api/                  # REST endpoints
├── alerts/               # ML, anomaly, rogue logic
├── c2/                   # Command bus (Serial/MQTT)
├── frontend/             # React GUI
├── README.md             # You're reading this
````


## 🌐 Captive Portal

* ESP32 launches SoftAP
* DNS redirects all domains to `192.168.4.1`
* Spoofed login page POSTs to ESP32 SPIFFS
* Transmitted to PC backend for display/storage


## 🧠 AI Model Flow

* RSSI patterns + MAC probes ingested to SQLite
* PyTorch-based LSTM analyzes for outliers
* Alerts generated via WebSocket
* GPU optional (LSTM speeds up w/ CUDA)

## 🧬 PC-Powered Attacks (TL-WN722N)

* Monitor Mode Packet Capture
* AP Clone + Handshake Harvesting (`aircrack-ng`)
* Deauth Flood (`aireplay-ng`, `hcxdumptool`)
* Real-time stream of attacks via WebSocket to UI
* Safety Toggle: `.env → ZEUSNET_MODE=SAFE|AGGRESSIVE`


## 🔌 Serial Command Protocol

| Opcode | Direction | Purpose                  |
| ------ | --------- | ------------------------ |
| 0x01   | PC→ESP    | Config scan settings     |
| 0x02   | PC→ESP    | Switch to captive portal |
| 0x10   | ESP→PC    | Send SSID scan list      |
| 0x11   | ESP→PC    | Send MAC probe list      |
| 0x12   | ESP→PC    | Portal form capture      |
| 0x30   | PC→ESP    | OTA firmware update      |

## ⚙️ Build Instructions

```bash
# Backend API
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# React UI
cd frontend && npm install && npm run dev

# ESP32 (via Arduino CLI)
arduino-cli compile -b esp32:esp32:esp32 esp32/zeusnet_esp32.ino
arduino-cli upload -p /dev/ttyUSB0 -b esp32:esp32:esp32
```

## 📦 Export & Backup

* `/api/export/csv` endpoint
* Daily cron job at 3am to archive scans:

```cron
0 3 * * * /usr/bin/python /srv/zeusnet/backend/export/backup.py >> /var/log/zeusnet_backup.log
```

## 🔐 Ethical Use Disclaimer

ZeusNet is provided **for educational and authorized penetration testing** only. Aggressive modules are disabled by default. All usage must comply with local laws and explicit permission from targets.

## 🧿 Join the Legion

ZeusNet is modular. More payloads coming soon:

* Bluetooth sniffing
* AI-enhanced face tagging
* USB HID injection (via dual role)
* Meshnet C2 via LoRa

> Built for chaos. Engineered for clarity. May your packets be ever invisible.

```

Let me know if you want it split across language files (e.g., `README.en.md`, `README.dev.md`, `README.ops.md`) or if we want dark mode terminal preview for GitHub.
```
