# ZEUSNET: Intelligent Agents Manifest

This document outlines all AI-driven Agents operating within the ZeusNet ecosystem. These agents follow a modular structure designed for autonomous collaboration, system orchestration, and network intelligence.

---

## 🧠 Agent Index

| Agent Name     | Type       | Description                                                                 | Entry Point / File              |
|----------------|------------|-----------------------------------------------------------------------------|----------------------------------|
| ZeusRelay      | MQTT Agent | Handles command relays over MQTT for remote control and status propagation. | `backend/agents/zeus_relay.py`  |
| SignalWatcher  | Sensor AI  | Monitors incoming RSSI/SSID data, filters noise, and logs signal events.    | `backend/agents/signal_watcher.py` |
| MapIntelligence| Visual AI  | Processes and maps live network events to a geospatial UI.                  | `backend/agents/map_intel.py`   |
| AnomalyGuard   | Defense AI | Flags unusual patterns in RSSI/network spikes for security analysis.        | `backend/agents/anomaly_guard.py` |
| CommandHub     | Core Agent | Accepts user/admin input, interprets intent, dispatches actions accordingly.| `backend/agents/command_hub.py` |

---

## 🔧 Agent Mode Options

Each agent supports the following optional modes via ENV or config:

| Option           | Description                                       | Default     |
|------------------|---------------------------------------------------|-------------|
| `DEBUG_MODE`     | Enables verbose logging and trace output          | `false`     |
| `ISOLATED_MODE`  | Runs the agent standalone, no inter-agent links   | `false`     |
| `RETRY_LIMIT`    | Max retries before escalation or fallback         | `3`         |
| `HOT_RELOAD`     | Auto-reloads code during development              | `true`      |

---

## 🧩 Agent Capabilities

- **Autonomous Execution**: Each agent operates independently but can collaborate via event bus or MQTT.
- **Plugin Awareness**: Agents can discover and leverage registered plugins (see `PLUGINS.md`).
- **Cross-Platform Compatibility**: Designed to run on Linux, macOS, Windows.
- **Observable**: Integrated with Prometheus metrics (see `OBSERVABILITY.md`).

---

## 🛠️ Integration Notes

- All agents are instantiated via the `AgentManager` (`backend/core/agent_manager.py`).
- Environment variables are loaded from `.env` or CLI args.
- Agents report heartbeat to `http://localhost:8000/heartbeat` by default.

---

## 🚧 Planned Agents

| Agent Name       | Type          | Status     | Description |
|------------------|---------------|------------|-------------|
| ReconBot         | Recon Agent   | ⚙️ Planned | Actively scans Wi-Fi landscape and records anomalies |
| IntelBroker      | Meta Agent    | ⚙️ Planned | Routes intelligence between agents and frontend      |
| ZeusCommander    | Master Agent  | ⚙️ Planned | Overarching task dispatcher for complex workflows    |

---

This manifest is used by ChatGPT Codex to understand agent responsibilities, entry points, and runtime options.

> **Maintainer:** God Of Code, Zeus  
> **Last Updated:** 2025-06-25
