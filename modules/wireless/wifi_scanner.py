import os
import subprocess
import re
from core.utils import Colors

class WiFiScanner:
    def __init__(self, interface=None):
        self.interface = interface or self.detect_interface()
        self.results = []
        
    def detect_interface(self):
        """Автоматическое определение беспроводного интерфейса"""
        try:
            ifaces = os.listdir('/sys/class/net')
            for iface in ['wlan0', 'wlan1', 'wlp2s0', 'wlp3s0', 'wifi0']:
                if iface in ifaces:
                    return iface
            return ifaces[0] if ifaces else None
        except:
            return None
            
    def scan(self, duration=10):
        """Сканирование Wi-Fi сетей"""
        if not self.interface:
            print(f"{Colors.RED}[-] No wireless interface found{Colors.RESET}")
            return []
            
        try:
            # Запуск сканирования
            subprocess.run(
                ['iw', self.interface, 'scan', 'duration', str(duration)],
                capture_output=True,
                text=True,
                timeout=duration + 2
            )
            
            # Получение результатов
            result = subprocess.check_output(
                ['iw', self.interface, 'scan', 'dump'],
                text=True
            )
            
            return self.parse_scan(result)
        except Exception as e:
            print(f"{Colors.RED}[-] Scan failed: {str(e)}{Colors.RESET}")
            return []
            
    def parse_scan(self, scan_data):
        """Парсинг результатов сканирования"""
        networks = []
        current = {}
        
        for line in scan_data.splitlines():
            # Новая сеть
            if 'BSS' in line:
                if current:
                    networks.append(current)
                    current = {}
                match = re.search(r'BSS (\w{2}(?::\w{2}){5})', line)
                if match:
                    current['bssid'] = match.group(1)
            
            # SSID
            elif 'SSID:' in line:
                match = re.search(r'SSID: (.+)$', line)
                if match:
                    current['ssid'] = match.group(1)
                    
            # Канал
            elif 'freq:' in line:
                match = re.search(r'freq: (\d+)', line)
                if match:
                    freq = int(match.group(1))
                    current['channel'] = (freq - 2407) // 5
                    
            # Мощность сигнала
            elif 'signal:' in line:
                match = re.search(r'signal: ([\d.-]+) dBm', line)
                if match:
                    current['signal'] = match.group(1)
                    
            # Защита
            elif 'capability:' in line:
                current['security'] = 'Open'
                if 'WPA' in line:
                    current['security'] = 'WPA'
                elif 'WEP' in line:
                    current['security'] = 'WEP'
                elif 'RSN' in line:
                    current['security'] = 'WPA2'
        
        if current:
            networks.append(current)
            
        return networks

def scan_networks():
    """Функция для вызова из AttackManager"""
    scanner = WiFiScanner()
    networks = scanner.scan()
    
    if not networks:
        print(f"{Colors.RED}[-] No networks found{Colors.RESET}")
        return
        
    # Вывод результатов
    print(f"{Colors.CYAN}{'SSID':<20} {'BSSID':<18} {'CH':>3} {'SIGNAL':>6} {'SECURITY':<8}{Colors.RESET}")
    print("-" * 60)
    
    for net in networks:
        ssid = net.get('ssid', 'Hidden')
        bssid = net.get('bssid', 'Unknown')
        channel = net.get('channel', '?')
        signal = net.get('signal', '-0')
        security = net.get('security', '?')
        
        print(f"{ssid:<20} {bssid:<18} {channel:>3} {signal:>6} dBm {security:<8}")