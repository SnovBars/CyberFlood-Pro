#!/bin/bash

# CyberFlood Pro Kali Nethunter Setup
# Version: 1.0
echo -e "\033[38;2;106;13;173m"
echo " ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██████╗ ██╗      ██████╗  ██████╗ ██████╗ "
echo "██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔══██╗"
echo "██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██████╔╝██║     ██║   ██║██║   ██║██║  ██║"
echo "██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██╗██║     ██║   ██║██║   ██║██║  ██║"
echo "╚██████╗   ██║   ██║  ██║███████╗██║  ██║██║  ██║███████╗╚██████╔╝╚██████╔╝██████╔╝"
echo " ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ "
echo -e "\033[0m"

echo "[*] Setting up Kali Nethunter environment for CyberFlood Pro"

# Обновление пакетов
sudo apt update -y
sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip git g++ build-essential libpcap-dev

# Установка Python зависимостей
pip3 install --upgrade pip
pip3 install requests dnspython scapy pybluez colorama psutil

# Компиляция C++ модулей
echo "[*] Compiling C++ attack modules..."
cd modules/layer4

g++ -O3 -Wall -static -std=c++17 -o syn_flood syn_flood.cpp
g++ -O3 -Wall -static -std=c++17 -o icmp_flood icmp_flood.cpp
g++ -O3 -Wall -static -std=c++17 -o udp_flood udp_flood.cpp

cd ../..

# Установка прав
chmod +x core/attack_manager.py
chmod +x core/api_server.py
chmod +x modules/layer4/*

echo -e "\033[32m[✓] Kali Nethunter setup completed successfully!\033[0m"
echo "Run: python3 core/attack_manager.py"