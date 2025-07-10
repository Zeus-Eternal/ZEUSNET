# Repository Guidelines

This project uses both Python and JavaScript/TypeScript. Keep the codebase clean and organized so that continuous integration (CI) runs smoothly.

## Directory layout

- `src/` contains Python source modules.
- `tests/` holds Python test suites executed with **pytest**.
- `js/` contains JavaScript/TypeScript sources. Tests for this code live in `js/__tests__/` and run with **jest**.
- Miscellaneous project documentation and configuration live in the repository root.

## Style

- Format Python code with **Black** and lint with **Ruff**.
- Format JavaScript/TypeScript with **Prettier**.
- Python files use 4 spaces per indent. JavaScript/TypeScript uses 2 spaces.

## Running tests

- Execute `pytest` from the repository root to run the Python test suite.
- Execute `npm test` in the `js/` directory to run the jest suite.

## CI expectations

Pull requests should pass all linting and test commands:

```bash
ruff .
black --check .
prettier --check "js/**/*.{js,ts}"
pytest
( cd js && npm test )
```

CI will fail if any of these steps fail. Ensure new code includes appropriate tests.

## Coding conventions

- Keep commit messages concise yet descriptive.
- Provide docstrings for all public Python classes and functions.
- Use type hints in new Python code where practical.
- Prefer descriptive variable names and avoid large functions; break complex logic into smaller helpers.
=======
# ZEUSNET • Intelligent Agents Manifest
*A single source-of-truth for every autonomous module in the ZeusNet arsenal.*

---

## 🧠 Agent Index

| Agent Name      | Type        | Description                                                                                   | Entry Point / File                           |
|-----------------|-------------|-----------------------------------------------------------------------------------------------|----------------------------------------------|
| ZeusRelay       | MQTT Agent  | Bridges MQTT ⇆ Serial traffic for remote command & control, status heartbeat propagation      | `backend/agents/zeus_relay.py`               |
| SignalWatcher   | Sensor AI   | Listens to ESP32 RSSI / SSID data, de-noises, timestamps and streams into the DB              | `backend/agents/signal_watcher.py`           |
| MapIntelligence | Visual AI   | Converts live network events into geo-referenced overlays for the UI heat-map                 | `backend/agents/map_intel.py`                |
| AnomalyGuard    | Defense AI  | Performs statistical / ML anomaly detection on signal metrics                                 | `backend/agents/anomaly_guard.py`            |
| CommandHub      | Core Agent  | Central intent router: interprets user inputs & dispatches tasks to other agents              | `backend/agents/command_hub.py`              |

---

## 🔧 Global Agent Mode Options

| Option            | Description                                              | Default |
|-------------------|----------------------------------------------------------|---------|
| `DEBUG_MODE`      | Verbose logging + trace packets                          | `false` |
| `ISOLATED_MODE`   | Run standalone (no inter-agent bus)                      | `false` |
| `RETRY_LIMIT`     | Max retries before escalation / fallback                 | `3`     |
| `HOT_RELOAD`      | Auto-reload code on file change (dev only)               | `true`  |

---

## 🧩 Shared Capabilities

- **Autonomous Execution** — each agent has its own asyncio task-loop
- **Plugin-Aware** — agents auto-discover plugins registered in `PLUGINS.md`
- **Cross-Platform** — Linux / macOS / Windows (where libs are available)
- **Observable** — Prometheus metrics via `/metrics` or Pushgateway

---

## 🛠 Integration Notes

- Agents instantiated by `AgentManager` → `backend/core/agent_manager.py`
- ENV loaded from `.env`, CLI flags override
- Heartbeats posted to `/heartbeat` every 15 s

---

# Agent Profiles
*(One section per agent – follow the template in the Style Guide)*

## 🧠 ZeusRelay
**Type**: `Controller`  
**ID**: `agent_zeusrelay`  
**Status**: 🟢 Active  
**Version**: `v1.0.0`  
**Scope**: `Local`  
**Visibility**: `Internal`

### 🎯 Purpose
Bridges serial frames from ESP32 nodes to the MQTT broker and vice-versa, providing a low-latency command pipeline and status fan-out.

### 🔧 Capabilities
- Serial ⇆ MQTT bidirectional relay
- Command opcode validation
- Automatic reconnection & QoS 1 delivery
- Optional TLS if MQTT is secured

### 📥 Inputs
| Source             | Format | Description                       |
|--------------------|--------|-----------------------------------|
| Serial (ESP32)     | JSON   | Raw scan / portal / cmd frames    |
| `zeusnet/to_esp`   | MQTT   | Remote command packets            |

### 📤 Outputs
| Destination             | Format | Description                   |
|-------------------------|--------|-------------------------------|
| `zeusnet/from_esp`      | MQTT   | Forwarded ESP32 messages      |
| Serial (ESP32)          | JSON   | Encoded opcode/ payload       |

### 🔗 Dependencies
- `pyserial`
- `paho-mqtt`

### 🧪 Test Commands
```bash
# Fire a dummy scan trigger
mosquitto_pub -t zeusnet/to_esp -m '{"opcode":1,"payload":{"scan":true}}'
````

---

## 🧠 SignalWatcher

**Type**: `Sensor`
**ID**: `agent_signalwatcher`
**Status**: 🟢 Active
**Version**: `v1.0.0`
**Scope**: `Local`
**Visibility**: `Internal`

### 🎯 Purpose

Consumes ESP32 Wi-Fi scan rows, filters duplicates / noise, batches them into the database and raises events for downstream analytics.

### 🔧 Capabilities

* Rolling RSSI average & debounce
* Batch insert to SQLite / Postgres
* Emits Prometheus metrics (`rssi_avg`, `ssid_seen_total`)
* Publishes “new SSID” events to MQTT

### 📥 Inputs

| Source             | Format | Description              |
| ------------------ | ------ | ------------------------ |
| `zeusnet/from_esp` | JSON   | Raw scan rows from ESP32 |

### 📤 Outputs

| Destination             | Format | Description                 |
| ----------------------- | ------ | --------------------------- |
| SQLite `wifi_scans`     | SQL    | Persistent scan records     |
| `zeusnet/signal_events` | MQTT   | Deduped / processed signals |

### 🔗 Dependencies

* `SQLAlchemy`
* `paho-mqtt`
* `prometheus-client`

### 🧪 Test Commands

```bash
mosquitto_pub -t zeusnet/from_esp -m '{"ssid":"Test","bssid":"aa:bb","rssi":-42,"timestamp":"..."}'
```

---

## 🧠 MapIntelligence

**Type**: `Synthesizer`
**ID**: `agent_mapintel`
**Status**: 🟢 Active
**Version**: `v1.0.0`
**Scope**: `Hybrid`
**Visibility**: `User-facing`

### 🎯 Purpose

Transforms processed signal events into GeoJSON heat-layers for the React or GTK front-end, enabling a real-time map overlay.

### 🔧 Capabilities

* SSID/BSSID ⇆ Geo-hash translation (if GPS present)
* Heat-map tile generation
* WebSocket broadcast to UI clients
* Caching with Redis

### 📥 Inputs

| Source                  | Format | Description           |
| ----------------------- | ------ | --------------------- |
| `zeusnet/signal_events` | MQTT   | Processed signal rows |

### 📤 Outputs

| Destination           | Format  | Description          |
| --------------------- | ------- | -------------------- |
| `/ws/map` (WebSocket) | GeoJSON | Live heat-map chunks |

### 🔗 Dependencies

* `fastapi_websocket_pubsub`
* `redis`

---

## 🧠 AnomalyGuard

**Type**: `Analyzer`
**ID**: `agent_anomalyguard`
**Status**: 🟢 Active
**Version**: `v1.0.0`
**Scope**: `Local`
**Visibility**: `User-facing`

### 🎯 Purpose

Runs statistical and ML checks over rolling RSSI, SSID and device metrics to flag rogue APs, clones, and abrupt signal drops.

### 🔧 Capabilities

* Z-score & IQR outlier detection
* LSTM-based temporal anomaly detection (GPU optional)
* Alert routing to `/api/alerts` & MQTT
* Auto-throttling to prevent alert storms

### 📥 Inputs

| Source              | Format | Description            |
| ------------------- | ------ | ---------------------- |
| SQLite `wifi_scans` | ORM    | Historical scan series |

### 📤 Outputs

| Destination       | Format | Description           |
| ----------------- | ------ | --------------------- |
| `alerts` DB table | SQL    | Persistent alerts     |
| `zeusnet/alerts`  | MQTT   | Realtime alert stream |

### 🔗 Dependencies

* `pandas`
* `torch`
* `scikit-learn`

### 🧪 Test Commands

```bash
curl -X POST http://localhost:8000/api/alerts/fake --data '{"type":"TEST","msg":"simulate"}'
```

---

## 🧠 CommandHub

**Type**: `Controller`
**ID**: `agent_commandhub`
**Status**: 🟢 Active
**Version**: `v1.0.0`
**Scope**: `Local`
**Visibility**: `User-facing`

### 🎯 Purpose

Serves as the single point of truth for user/admin commands, interprets natural-language intents (phase 3) and dispatches structured opcodes to appropriate agents.

### 🔧 Capabilities

* REST + WebSocket intake
* Intent parser / CLI dispatcher
* Secure permission checks
* Audit log of all admin actions

### 📥 Inputs

| Source              | Format | Description    |
| ------------------- | ------ | -------------- |
| REST `/api/command` | JSON   | Command blocks |

### 📤 Outputs

| Destination      | Format | Description           |
| ---------------- | ------ | --------------------- |
| `zeusnet/to_esp` | MQTT   | Serial opcode payload |
| In-memory queue  | Dict   | Agent dispatch tasks  |

### 🔗 Dependencies

* `fastapi`
* `pydantic`

### 🧪 Test Commands

```bash
curl -X POST http://localhost:8000/api/command -d '{"opcode":1,"payload":{"scan":true}}'
```

---

## 🚧 Planned Agents

| Agent Name    | Type         | Status     | Description                                      |
| ------------- | ------------ | ---------- | ------------------------------------------------ |
| ReconBot      | Recon Agent  | ⚙️ Planned | Actively sweeps all channels & logs new BSSIDs   |
| IntelBroker   | Meta Agent   | ⚙️ Planned | Aggregates intel from multiple ZeusNet instances |
| ZeusCommander | Master Agent | ⚙️ Planned | Multi-node orchestration & advanced task graph   |

---

# 🎨 Style Guide for Future Entries

*(Codex parses this section; do **not** change header names without updating tooling.)*

### 1  Agent Index Row

```markdown
| AgentName | AgentType | Short description (max 90 chars) | `backend/agents/file.py` |
```

### 2  Full Agent Profile Template

*(Copy → paste → replace placeholders)*

````markdown
## 🧠 AgentName
**Type**: `[Sensor | Controller | Analyzer | Synthesizer | Plugin]`  
**ID**: `agent_agentname`  
**Status**: 🟢 Active  
**Version**: `vX.Y.Z`  
**Scope**: `Local | Remote | Hybrid`  
**Visibility**: `User-facing | Internal | Experimental`

### 🎯 Purpose
> One-sentence clear description.

### 🔧 Capabilities
- Bullet list

### 📥 Inputs
| Source | Format | Description |
|--------|--------|-------------|

### 📤 Outputs
| Destination | Format | Description |

### 🔗 Dependencies
- list…

### 🧪 Test Commands
```bash
# example command
````

```

### 3  Status Emoji
| Emoji | Meaning |
|-------|---------|
| 🟢   | Active  |
| 🔴   | Inactive/Deprecated |
| ⚙️    | Planned/In Dev |

---

> **Maintainer:** God Of Code (Zeus)  
> **Last Updated:** 2025-06-25
```

