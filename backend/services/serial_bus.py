import time
import json
import logging

MAX_CONSECUTIVE_ERRORS = 5
ERROR_BACKOFF_SEC = 2

class SerialBus:
    def __init__(self, port, baudrate=115200):
        import serial
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.error_count = 0

    def read_loop(self, on_data):
        while True:
            try:
                line = self.ser.readline()
                if not line:
                    logging.error("[SerialBus] Read error: empty line or device not responding")
                    self.error_count += 1
                    self._maybe_backoff()
                    continue

                # Try decode
                try:
                    # Decode bytes to str if needed
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    if not line_str:
                        raise ValueError("Empty line after decode")
                    data = json.loads(line_str)
                    self.error_count = 0
                    on_data(data)
                except json.JSONDecodeError as e:
                    logging.error(f"[SerialBus] JSON decode error: {e} | Raw: {repr(line)}")
                    self.error_count += 1
                    self._maybe_backoff()
                except Exception as e:
                    logging.error(f"[SerialBus] General decode error: {e} | Raw: {repr(line)}")
                    self.error_count += 1
                    self._maybe_backoff()
            except Exception as e:
                logging.critical(f"[SerialBus] FATAL: {e}")
                self.error_count += 1
                self._maybe_backoff()

    def _maybe_backoff(self):
        if self.error_count >= MAX_CONSECUTIVE_ERRORS:
            logging.critical(f"[SerialBus] {self.error_count} consecutive errors, backing off for {ERROR_BACKOFF_SEC}s")
            time.sleep(ERROR_BACKOFF_SEC)
            self.error_count = 0  # Reset so we don't stall forever
