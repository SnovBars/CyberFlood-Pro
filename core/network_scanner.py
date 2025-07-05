import os
import platform
import subprocess
import re
from .utils import Colors

class NetworkScanner:
    def __init__(self):
        self.platform = platform.system().lower()

    def scan(self, subnet):
        """Сканирует сеть и возвращает найденные устройства"""
        if self.platform == "linux" or "android" in self.platform:
            return self._arp_scan(subnet)
        elif self.platform == "windows":
            return self._arp_scan_windows(subnet)
        else:
            print(f"{Colors.RED}[-] Network scanning not supported on {self.platform}{Colors.RESET}")
            return {}

    def _arp_scan(self, subnet):
        """ARP сканирование для Linux/Android"""
        devices = {}
        
        try:
            # Используем arp-scan если доступен
            result = subprocess.check_output(
                ["arp-scan", "-l", "-g", subnet],
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Парсим вывод arp-scan
            for line in result.splitlines():
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 2 and re.match(r'\d+\.\d+\.\d+\.\d+', parts[0]):
                    ip, mac = parts[0], parts[1]
                    if mac != "00:00:00:00:00:00":
                        devices[ip] = mac
                        
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Альтернативный метод через arp
            result = subprocess.check_output(["arp", "-a"], text=True)
            
            for line in result.splitlines():
                match = re.search(r'(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F:]{17})', line)
                if match:
                    ip, mac = match.groups()
                    devices[ip] = mac
        
        return devices

    def _arp_scan_windows(self, subnet):
        """ARP сканирование для Windows"""
        devices = {}
        
        try:
            # Получаем таблицу ARP
            result = subprocess.check_output(
                ["arp", "-a"],
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Парсим вывод arp -a
            for line in result.splitlines():
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]{17})', line)
                if match:
                    ip, mac = match.groups()
                    mac = mac.replace('-', ':')
                    devices[ip] = mac
        
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}[-] ARP scan failed: {e.output}{Colors.RESET}")
            
        return devices

    def ping_sweep(self, subnet):
        """Пинг-сканирование сети"""
        devices = {}
        
        # Определяем диапазон IP
        base_ip = ".".join(subnet.split('.')[:3])
        
        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            if self._ping(ip):
                devices[ip] = "Unknown"
                
        return devices

    def _ping(self, ip):
        """Проверяет доступность хоста"""
        param = "-n 1" if platform.system().lower() == "windows" else "-c 1 -W 1"
        command = f"ping {param} {ip}"
        
        try:
            output = subprocess.check_output(
                command, 
                shell=True, 
                stderr=subprocess.STDOUT
            )
            return True
        except subprocess.CalledProcessError:
            return False