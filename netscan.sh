l#!/bin/bash

echo "--- Nearby Wi-Fi Networks ---"
# Note: Termux cannot see nearby SSIDs without root/Termux:API.
# This checks if you are at least connected.
if command -v termux-wifi-scaninfo &> /dev/null; then
    termux-wifi-scaninfo | grep "ssid" | wc -l
    echo "Networks found via Termux:API"
else
    echo "Install 'Termux:API' app and 'pkg install termux-api' to see nearby SSIDs."
fi

echo -e "\n--- Devices on Local Network ---"
# Get your local IP range (e.g., 192.168.1.0/24)
GATEWAY=$(ip route | grep default | awk '{print $3}')
if [ -z "$GATEWAY" ]; then
    echo "Not connected to a network."
    exit 1
fi
SUBNET=$(echo $GATEWAY | cut -d. -f1-3).0/24

echo "Scanning $SUBNET..."
# Nmap is the best way to find devices without root in Termux
nmap -sn $SUBNET | grep "Nmap scan report" | awk '{print $NF}'

