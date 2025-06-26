# ⚡ ZEUSNET: Wi‑Fi Recon & Pentest Intelligence Node

**Hybrid ESP32 + PC Tactical Framework for Cyber‑Network Diagnostics**

> ZeusNet is an advanced, modular Wi‑Fi surveillance and penetration testing suite. Powered by a USB‑tethered ESP32 and a high‑performance PC (RTX2080 Super + i7‑11700KF), it merges real‑time signal analytics, device tracking, and AI‑powered anomaly detection into a single unified toolkit.

## 🔧 Features

| Feature                      | Description                                      |
|-----------------------------|--------------------------------------------------|
| 🌐 Captive Portal trap       | ESP32-hosted login splash for phishing emulation |
| 📡 MAC-based device tracking | Tracks known devices across time/geolocation     |
| 🧠 AI anomaly detection      | Predicts unusual signal behavior with LSTM       |
| 🕵️ Rogue AP detection       | Flags SSID duplicates with different BSSIDs      |
| 📁 Auto backups              | Daily JSON/CSV dump of scan logs                 |
| 📊 Export to CSV/Excel       | Export tables directly from the GTK UI             |
| 🔥 Deauth & AP cloning       | Enabled via TL‑WN722N NIC in aggressive mode     |
| 🧪 TL‑WN722N automation      | Controlled packet injection, handshake captures  |
| 🗺️ Heatmap dashboard         | Leaflet-powered map view in GTK UI |
| 🎛️ In-app pentest controls  | Toggle mode and launch attacks via UI |
| 📜 Advanced network list     | Filter scans by SSID or auth mode |
| 📈 Signal charts             | Top RSSI graph in Dashboard tab |

## 🧠 Architecture

```text
ESP32 (Spectral Scanner / Captive Portal)
  ⮕ USB Serial
      ⮕ FastAPI WarCore (Python 3.10+, PyTorch, Scapy, SQLite)
        ⮕ MQTT / WebSocket Bus
          ⮕ GTK Frontend + Dashboards
          ⮕ Optional: TL-WN722N (Monitor / Injection)
````

## 🚀 Quick Start

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# Tables are created automatically on first run
```

### Frontend (GTK)

```bash
python frontend/main.py
```

### Web UI (React)

```bash
cd webui
npm install
npm run dev
```

### Cross-Platform Docker MQTT

To avoid installing Mosquitto manually, run it via Docker:

```bash
docker compose up -d mqtt
```

Then launch everything with `start-zeusnet.sh` (or `.bat` on Windows). See
`docs/setup.md` for full setup instructions.

### GTK Desktop UI

For a native desktop view with tabs for networks, dashboards and map,
run the GTK app:

```bash
python frontend/main.py
```

This requires the `PyGObject` package built with GTK **4**.
If upgrading from an older GTK 3 build, remove any references to
`Gtk.ApplicationFlags.DEFAULT_FLAGS` or other deprecated APIs—GTK 4
no longer exposes these constants.
The window now shows a network table with filters, attack panel, a
dashboard graph of top RSSI values and a heatmap tab. Controls let you
change scan interval, toggle scanning, switch modes or select the serial
port. A status bar reports the last successful update or any errors.

### Auto Start with systemd (Linux)

For persistent operation, install the provided service file:

```bash
sudo cp systemd/zeusnet-serial.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable zeusnet-serial
sudo systemctl start zeusnet-serial
```

The service uses a cached serial port stored under `~/.config/zeusnet/last_serial`.
### Flash ESP32

```bash
arduino-cli compile -b esp32:esp32:esp32 esp32/zeusnet_esp32.ino
arduino-cli upload -p /dev/ttyUSB0 -b esp32:esp32:esp32
```

## 🧬 Serial Command Reference

| Code   | Direction | Purpose                        |
| ------ | --------- | ------------------------------ |
| `0x01` | PC → ESP  | Set config (interval, channel) |
| `0x02` | PC → ESP  | Switch to fake AP mode         |
| `0x10` | ESP → PC  | Send scan list (SSID/RSSI)     |
| `0x12` | ESP → PC  | Captive form POST              |
| `0x20` | PC → ESP  | Reboot ESP32                   |

## 📂 Folder Structure

```bash
ZeusNet/
├── esp32/                # ESP32 .ino sketches
├── backend/              # FastAPI core
│   ├── api/              # Scan, device, export endpoints
│   ├── alerts/           # Anomaly detection, MAC tracker
│   └── c2/               # Command bus
├── frontend/             # GTK UI
│   └── main.py          # Desktop application
├── webui/                # React web interface
```

## ⚠️ Mode Switching

Copy `.env.example` to `.env` to toggle behavior:

```env
ZEUSNET_MODE=SAFE
# Change to AGGRESSIVE to unlock full pentest features
```

> **SAFE Mode** disables any packet injection or spoofing.
> **AGGRESSIVE Mode** activates deauth, rogue AP, and swarm tactics (for legal use only).

### Environment Variables

| Variable      | Purpose                                | Default |
|---------------|----------------------------------------|---------|
| `RETRY_LIMIT` | Serial read errors before reconnecting | `3`     |

Call `GET /api/settings` to view current mode and serial configuration. Use
`POST /api/settings` with `{"mode": "AGGRESSIVE"}` to switch modes at runtime.

## 🛰️ TL-WN722N Tools

| Tool                | Role                         |
| ------------------- | ---------------------------- |
| `aircrack-ng`       | Handshake harvesting         |
| `hostapd + dnsmasq` | Rogue AP with captive portal |
| `hcxtools`          | PMKID capture                |
| `Scapy`             | Frame injection engine       |

Use via API call:

```http
POST /api/nic/attack
{
  "mode": "deauth",
  "target": "AA:BB:CC:DD:EE:FF",
  "channel": 6
}
```
Additional modes such as `survey` and `jam` provide blue‑team defensive actions.

## 🗃️ Backup Job (Linux crontab)

```cron
0 3 * * * /usr/bin/python3 /srv/zeusnet/backend/export/backup.py
```

Creates daily backup in `/backups/net_scan_YYYYMMDD.csv.gz`

## 🧙 AI Model (Optional)

Phase 2+ enables LSTM anomaly detection on RSSI trends.

```python
from torch import nn
class RSSIPredictor(nn.Module):
    ...
```

Flags dropouts, rogue clones, new MACs. Run on GPU if available.

## 📜 License

MIT for tools. Aggressive modules must comply with **your local laws**. This tool is for **education and authorized testing** only.

> "Observe silently. Analyze ruthlessly. Dominate ethically."
> — *ZeusNet WarCore, Operational Directive*

