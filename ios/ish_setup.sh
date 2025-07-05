#!/bin/ash

# CyberFlood Pro iSH Setup
# Version: 1.0
echo -e "\033[38;2;106;13;173m"
echo " ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██████╗ ██╗      ██████╗  ██████╗ ██████╗ "
echo "██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔══██╗"
echo "██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██████╔╝██║     ██║   ██║██║   ██║██║  ██║"
echo "██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██╗██║     ██║   ██║██║   ██║██║  ██║"
echo "╚██████╗   ██║   ██║  ██║███████╗██║  ██║██║  ██║███████╗╚██████╔╝╚██████╔╝██████╔╝"
echo " ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ "
echo -e "\033[0m"

echo "[*] Setting up iSH environment for CyberFlood Pro"

# Установка необходимых пакетов
apk update
apk add python3 py3-pip git g++ make linux-headers musl-dev openssl-dev libffi-dev

# Установка Python зависимостей
pip3 install --upgrade pip
pip3 install requests dnspython scapy-python3 colorama psutil

# Компиляция C++ модулей (статическая линковка)
echo "[*] Compiling C++ attack modules..."
cd modules/layer4

# Компиляция с использованием g++ для Alpine Linux
g++ -O3 -Wall -static -std=c++17 -pthread -o syn_flood syn_flood.cpp
g++ -O3 -Wall -static -std=c++17 -pthread -o icmp_flood icmp_flood.cpp
g++ -O3 -Wall -static -std=c++17 -pthread -o udp_flood udp_flood.cpp

cd ../..

# Установка прав
chmod +x core/attack_manager.py
chmod +x core/api_server.py
chmod +x modules/layer4/*

# Настройка сети (требует разрешения)
echo "[*] Configuring network settings..."
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

echo -e "\033[32m[✓] iSH setup completed successfully!\033[0m"
echo "Run: python3 core/attack_manager.py"
echo "Note: Some features may require Full iSH Version"