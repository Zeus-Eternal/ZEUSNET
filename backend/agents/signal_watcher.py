import logging
import time
import threading
import queue
from typing import Any

from backend.models import WiFiScan
from backend.db import SessionLocal
from backend.c2.command_bus import SerialCommandBus

# ESP32 opcode for Wi-Fi scan rows
OPCODE_SCAN_RESULT = 0x10

logger = logging.getLogger("signal_watcher")


class SignalWatcher:
    """Collect scan frames from SerialCommandBus and persist to DB."""

    def __init__(self, bus: SerialCommandBus, batch_size: int = 20, flush_interval: float = 1.0):
        self.bus = bus
        self.queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.running = False

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.bus.register_listener(self.on_packet)
        self.thread.start()
        logger.info("[SignalWatcher] started")

    def on_packet(self, data: dict[str, Any]) -> None:
        if data.get("opcode") == OPCODE_SCAN_RESULT:
            payload = data.get("payload") or {}
            self.queue.put(payload)

    def _loop(self) -> None:
        buffer: list[dict[str, Any]] = []
        last_flush = time.time()
        while self.running:
            try:
                item = self.queue.get(timeout=0.2)
                buffer.append(item)
            except queue.Empty:
                pass

            now = time.time()
            if buffer and (len(buffer) >= self.batch_size or now - last_flush >= self.flush_interval):
                self._flush(buffer)
                buffer.clear()
                last_flush = now

    def _flush(self, items: list[dict[str, Any]]) -> None:
        session = SessionLocal()
        try:
            for it in items:
                scan = WiFiScan(
                    ssid=it.get("ssid", ""),
                    bssid=it.get("bssid", ""),
                    rssi=it.get("rssi", 0),
                    auth=it.get("auth", ""),
                    channel=it.get("channel", 0),
                )
                session.add(scan)
            session.commit()
            logger.debug(f"[SignalWatcher] inserted {len(items)} scans")
        except Exception as e:
            session.rollback()
            logger.error(f"[SignalWatcher] DB error: {e}")
        finally:
            session.close()
