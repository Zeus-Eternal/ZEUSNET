import time
import json
import logging
import serial

logger = logging.getLogger(__name__)

MAX_CONSECUTIVE_ERRORS = 5
ERROR_BACKOFF_SEC = 2


def safe_parse_serial_line(raw: bytes) -> dict | None:
    try:
        decoded = raw.decode("utf-8").strip()
        if not decoded:
            return None
        return json.loads(decoded)
    except json.JSONDecodeError as e:
        logger.warning(f"[SerialBus] JSON parse error: {e} | Raw: {raw}")
        return None


class SerialBus:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.error_count = 0

    def read_loop(self, on_data):
        while True:
            try:
                raw = self.ser.readline()

                if not raw:
                    logger.error(
                        "[SerialBus] Read error: empty line or device not responding"
                    )
                    self._increment_error()
                    continue

                parsed = safe_parse_serial_line(raw)
                if parsed:
                    self.error_count = 0
                    on_data(parsed)
                else:
                    self._increment_error()
            except Exception as e:
                logger.critical(f"[SerialBus] FATAL: {e}")
                self._increment_error()

    def _increment_error(self):
        self.error_count += 1
        if self.error_count >= MAX_CONSECUTIVE_ERRORS:
            logger.critical(
                f"[SerialBus] {self.error_count} consecutive errors, backing off for {ERROR_BACKOFF_SEC}s"
            )
            time.sleep(ERROR_BACKOFF_SEC)
            self.error_count = 0
