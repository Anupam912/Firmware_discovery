from scapy.all import sniff, IP, TCP

# Packet sniffer to analyze network traffic
def packet_callback(packet):
    if IP in packet and TCP in packet:
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        payload = packet[TCP].payload
        print(f"Packet {ip_src} -> {ip_dst}: {payload}")

# Capture packets from the specified interface
def start_packet_sniffing(interface="eth0"):
    sniff(iface=interface, filter="tcp", prn=packet_callback, store=0)
