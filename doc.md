# 🧠 ZeusNet Documentation

> **“Observe everything. Trigger nothing.”**

ZeusNet is a hybrid reconnaissance system using an ESP32-WROOM node tethered to a high-performance PC. Together, they form a **coordinated command, surveillance, and anomaly detection system** for ethical network penetration testing and environment awareness.

---

## ⚙️ Configuration

All configurations are managed through a `.env` file in the root of the backend directory.

### `.env` Example

```ini
# === General ===
ZEUSNET_MODE=SAFE               # Options: SAFE, AGGRESSIVE
PORT=/dev/ttyUSB0               # Serial port for ESP32
BAUD_RATE=921600                # Baud rate for serial comm
SCAN_INTERVAL=10                # Seconds between scans
EXPORT_DIR=backups              # Folder for auto-export

# === WebSocket ===
WS_ENABLED=True
WS_HOST=0.0.0.0
WS_PORT=8765

# === MQTT (optional) ===
MQTT_ENABLED=False
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=zeusnet/events

# === AI Settings ===
AI_MODEL=lstm
ANOMALY_THRESHOLD=0.75

# === Captive Portal ===
PORTAL_SSID=FreeWiFi_Public
PORTAL_PASSWORD=12345678
PORTAL_PAGE=login.html
```

---

## 🔁 Operational Modes

| Mode         | Description                                                                                                      |
| ------------ | ---------------------------------------------------------------------------------------------------------------- |
| `SAFE`       | Only passive scanning and logging. Deauth, spoofing, and injection are **disabled**.                             |
| `AGGRESSIVE` | Enables active modules: beacon swarm, deauth, portal hijack, and AP clone. Intended for authorized testing only. |

Change modes by editing the `.env`:

```ini
ZEUSNET_MODE=AGGRESSIVE
```

---

## 🛰️ ESP32 Communication Protocol

ZeusNet uses a binary serial command bus between the PC and ESP32:

| Opcode | From → To | Description                |
| ------ | --------- | -------------------------- |
| 0x01   | PC → ESP  | Set scan settings          |
| 0x02   | PC → ESP  | Start captive portal       |
| 0x10   | ESP → PC  | Transmit SSID scan results |
| 0x11   | ESP → PC  | Transmit MAC probe results |
| 0x12   | ESP → PC  | Captive portal form data   |
| 0x30   | PC → ESP  | OTA firmware update        |

---

## 🔒 Ethical Pentesting Usage

> **Important:** ZeusNet is designed strictly for **authorized security testing**. Use only on networks you own or are authorized to assess.

To ensure compliance:

* Keep `ZEUSNET_MODE=SAFE` unless explicitly authorized.
* Log all attack modules with timestamps.
* Enable `AGGRESSIVE` mode only in a controlled test environment.

---

## 📦 Export & Logs

All logs are timestamped and stored as CSV and JSON by default.

### Manual Export

```http
GET /api/export/csv
```

### Scheduled Backups

```cron
0 3 * * * /usr/bin/python3 /srv/zeusnet/backend/export/backup.py >> /var/log/zeusnet_backup.log
```

---

## 🧠 AI Detection Modules

AI models monitor signal and device behavior for anomalies:

| Model     | Type    | Function                                 |
| --------- | ------- | ---------------------------------------- |
| LSTM      | PyTorch | Detects sudden signal drops/spikes       |
| DBSCAN    | Sklearn | Clusters MAC patterns to find outliers   |
| Heuristic | Custom  | Flags rogue APs, frequent probe requests |

---

## 🧬 Future Configuration Flags

| Flag/Var                | Description                                 |
| ----------------------- | ------------------------------------------- |
| `AI_MODEL`              | Switch between models: lstm, dbscan, hybrid |
| `EXPORT_FORMAT`         | Options: csv, json, both                    |
| `ENABLE_PORTAL_LOGGING` | Toggle logging of spoofed logins            |
| `DISABLE_GPU`           | Forces CPU-only ML model evaluation         |
| `BEACON_INTERVAL_MS`    | Controls ESP32 beacon spam rate             |

---

## 🧠 AI + GPU (Optional)

When `torch.cuda.is_available()` returns `True`, ZeusNet will automatically:

* Offload LSTM model to GPU
* Batch process signal input with higher resolution
* Store historical activations for long-term analysis

Use `.env` flag to disable GPU:

```ini
DISABLE_GPU=True
```

---

## 🧿 WebSocket Events

All real-time alerts and scan results are sent via WebSocket if enabled.

| Event Type       | Payload                        |
| ---------------- | ------------------------------ |
| `ssid_scan`      | List of SSIDs and RSSI         |
| `mac_probe`      | MAC address & timestamps       |
| `rogue_ap_alert` | SSID + conflicting BSSID alert |
| `portal_trigger` | Captive login POST form        |

---

## 📁 Project Folder Summary

```plaintext
ZeusNet/
├── .env                  # Config and operational mode
├── backend/              # FastAPI core + AI logic
├── api/                  # REST endpoints
├── esp32/                # ESP32 code (Arduino/IDF)
├── alerts/               # AI models + rogue detection
├── c2/                   # Command bus (serial + MQTT)
├── frontend/             # React + WebSocket GUI
├── backups/              # Daily exported logs
└── README.md             # Public-facing documentation
```

---

Let me know if you'd like an advanced **admin cheatsheet**, **attack module reference guide**, or a **dark-mode doc site** to match this documentation! 😈
