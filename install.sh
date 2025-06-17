#!/bin/bash

# CyberFlood-Pro Installer
# Version: 1.0
echo -e "\033[38;2;106;13;173m"
echo " ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██████╗ ██╗      ██████╗  ██████╗ ██████╗ "
echo "██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔══██╗"
echo "██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██████╔╝██║     ██║   ██║██║   ██║██║  ██║"
echo "██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██╗██║     ██║   ██║██║   ██║██║  ██║"
echo "╚██████╗   ██║   ██║  ██║███████╗██║  ██║██║  ██║███████╗╚██████╔╝╚██████╔╝██████╔╝"
echo " ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ "
echo -e "\033[0m"

echo "[*] Installing CyberFlood Pro DDoS Framework"
echo "[*] Detecting platform..."

# Определение платформы
if [[ "$OSTYPE" == "linux-android"* ]]; then
    echo "[+] Android (Termux) detected"
    chmod +x android/termux_setup.sh
    ./android/termux_setup.sh
    
elif [[ "$(uname -s)" == "Linux" ]]; then
    if grep -q "kali" /etc/os-release; then
        echo "[+] Kali Linux (Nethunter) detected"
        chmod +x android/nethunter_setup.sh
        ./android/nethunter_setup.sh
    else
        echo "[+] Linux detected"
        sudo apt update
        sudo apt install -y python3 python3-pip git g++ make libpcap-dev
        pip3 install -r requirements.txt
        cd modules/layer4
        make
        cd ../..
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[-] macOS installation not supported"
    exit 1

elif [[ "$(uname -s)" == "Windows" || "$(uname -s)" == "MINGW"* ]]; then
    echo "[+] Windows detected"
    pip install -r requirements.txt
    echo "[!] C++ modules require manual compilation with Visual Studio"

elif [[ "$(uname -s)" == "ish"* ]]; then
    echo "[+] iOS (iSH) detected"
    chmod +x ios/ish_setup.sh
    ./ios/ish_setup.sh

else
    echo "[-] Unsupported platform: $OSTYPE"
    exit 1
fi

echo -e "\033[32m[✓] Installation completed successfully!\033[0m"
echo "Run: python core/attack_manager.py --help"