#!/data/data/com.termux/files/usr/bin/bash

# CyberFlood Pro Termux Setup
# Version: 1.0
echo -e "\033[38;2;106;13;173m"
echo " ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██████╗ ██╗      ██████╗  ██████╗ ██████╗ "
echo "██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔══██╗"
echo "██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██████╔╝██║     ██║   ██║██║   ██║██║  ██║"
echo "██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██╗██║     ██║   ██║██║   ██║██║  ██║"
echo "╚██████╗   ██║   ██║  ██║███████╗██║  ██║██║  ██║███████╗╚██████╔╝╚██████╔╝██████╔╝"
echo " ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ "
echo -e "\033[0m"

echo "[*] Setting up Termux environment for CyberFlood Pro"

# Обновление пакетов
pkg update -y
pkg upgrade -y

# Установка необходимых пакетов
pkg install -y python clang git openssl libffi rust make ndk-multilib

# Установка Python зависимостей
pip install --upgrade pip
pip install requests dnspython scapy-python3 pybluez colorama psutil

# Компиляция C++ модулей
echo "[*] Compiling C++ attack modules..."
cd modules/layer4

# Компиляция с использованием Clang для Android
clang++ -O3 -Wall -static -std=c++17 -o syn_flood syn_flood.cpp
clang++ -O3 -Wall -static -std=c++17 -o icmp_flood icmp_flood.cpp
clang++ -O3 -Wall -static -std=c++17 -o udp_flood udp_flood.cpp

cd ../..

# Установка прав
chmod +x core/attack_manager.py
chmod +x core/api_server.py
chmod +x modules/layer4/*

# Создание ярлыка для запуска
echo "alias cyberflood='python $PWD/core/attack_manager.py'" >> $HOME/.bashrc
echo "alias cf-api='python $PWD/core/api_server.py'" >> $HOME/.bashrc

echo -e "\033[32m[✓] Termux setup completed successfully!\033[0m"
echo "Run: python core/attack_manager.py"
echo "Or use: cyberflood"