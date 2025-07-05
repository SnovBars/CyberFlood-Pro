import os
import sys
import importlib.util
import threading
import time
from .utils import detect_platform, Colors, print_banner
from .network_scanner import NetworkScanner

class AttackManager:
    def __init__(self):
        self.platform = detect_platform()
        self.attacks = self.load_attacks()
        self.active_attacks = {}
        self.scanner = NetworkScanner()
        
    def load_attacks(self):
        """Динамически загружает все доступные модули атак"""
        attacks = {}
        attack_types = ["layer4", "layer7", "wireless"]  # Включаем папку wireless
        
        for attack_type in attack_types:
            module_path = os.path.join("modules", attack_type)
            if not os.path.exists(module_path):
                print(f"{Colors.YELLOW}[!] Attack type not found: {attack_type}{Colors.RESET}")
                continue
                
            for file in os.listdir(module_path):
                if file.endswith('.py') and not file.startswith('__'):
                    module_name = file[:-3]
                    try:
                        spec = importlib.util.spec_from_file_location(
                            module_name, 
                            os.path.join(module_path, file)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        attacks[module_name] = module
                        print(f"{Colors.GREEN}[+] Loaded attack: {module_name}{Colors.RESET}")
                    except Exception as e:
                        print(f"{Colors.RED}[-] Error loading {file}: {str(e)}{Colors.RESET}")
        
        return attacks
    
    def start_attack(self, attack_name, target, power=1, duration=60, **kwargs):
        """Запускает указанную атаку"""
        if attack_name not in self.attacks:
            print(f"{Colors.RED}[-] Attack not available: {attack_name}{Colors.RESET}")
            return False
            
        if attack_name in self.active_attacks:
            print(f"{Colors.YELLOW}[!] Attack already running{Colors.RESET}")
            return False
            
        try:
            # Создаем поток для атаки
            stop_event = threading.Event()
            thread = threading.Thread(
                target=self.attacks[attack_name].start,
                args=(target, power, duration, stop_event),
                kwargs=kwargs,
                daemon=True
            )
            
            self.active_attacks[attack_name] = {
                "thread": thread,
                "stop_event": stop_event,
                "start_time": time.time(),
                "target": target,
                "power": power
            }
            
            thread.start()
            print(f"{Colors.CYAN}[+] Started {attack_name} against {target}{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.RED}[-] Failed to start attack: {str(e)}{Colors.RESET}")
            return False

    def stop_attack(self, attack_name):
        """Останавливает указанную атаку"""
        if attack_name not in self.active_attacks:
            print(f"{Colors.RED}[-] No active attack: {attack_name}{Colors.RESET}")
            return False
            
        try:
            self.active_attacks[attack_name]["stop_event"].set()
            self.active_attacks[attack_name]["thread"].join(timeout=5)
            del self.active_attacks[attack_name]
            print(f"{Colors.GREEN}[✓] Stopped {attack_name}{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.RED}[-] Failed to stop attack: {str(e)}{Colors.RESET}")
            return False

    def stop_all_attacks(self):
        """Останавливает все активные атаки"""
        for attack_name in list(self.active_attacks.keys()):
            self.stop_attack(attack_name)

    def list_attacks(self):
        """Выводит список доступных атак"""
        print(f"\n{Colors.ORANGE}Available Attacks:{Colors.RESET}")
        for i, attack in enumerate(self.attacks.keys(), 1):
            print(f"  {i}. {attack}")
        print()

    def status(self):
        """Показывает статус активных атак"""
        if not self.active_attacks:
            print(f"{Colors.YELLOW}[!] No active attacks{Colors.RESET}")
            return
            
        print(f"\n{Colors.ORANGE}Active Attacks:{Colors.RESET}")
        for i, (name, data) in enumerate(self.active_attacks.items(), 1):
            elapsed = time.time() - data["start_time"]
            print(f"  {i}. {name} -> {data['target']} (power: {data['power']}, time: {int(elapsed)}s)")
        print()

    def scan_network(self, subnet="192.168.1.0/24"):
        """Сканирует сеть на наличие устройств"""
        print(f"{Colors.CYAN}[*] Scanning network {subnet}...{Colors.RESET}")
        devices = self.scanner.scan(subnet)
        
        if not devices:
            print(f"{Colors.RED}[-] No devices found{Colors.RESET}")
            return
            
        print(f"\n{Colors.ORANGE}Network Devices:{Colors.RESET}")
        for i, (ip, mac) in enumerate(devices.items(), 1):
            print(f"  {i}. {ip} - {mac}")
        print()
    
    def scan_wifi_networks(self):
        """Сканирует Wi-Fi сети"""
        if not self.attacks.get('wifi_scanner'):
            print(f"{Colors.RED}[-] Wi-Fi scanner not available{Colors.RESET}")
            return
            
        try:
            # Используем модуль wifi_scanner
            self.attacks['wifi_scanner'].scan_networks()
        except Exception as e:
            print(f"{Colors.RED}[-] Wi-Fi scan failed: {str(e)}{Colors.RESET}")

def main():
    manager = AttackManager()
    
    # Обработка аргументов командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            manager.list_attacks()
            return
            
        if len(sys.argv) < 3:
            print("Usage: python attack_manager.py <attack> <target> [power] [duration]")
            print("Example: python attack_manager.py http_flood https://example.com 3 60")
            return
            
        attack = sys.argv[1]
        target = sys.argv[2]
        power = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
        
        manager.start_attack(attack, target, power, duration)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_all_attacks()
    else:
        # Интерактивный режим
        print_banner()
        print(f"{Colors.CYAN}CyberFlood Pro Attack Manager{Colors.RESET}")
        print(f"Platform: {manager.platform}\n")
        
        # iOS-specific initialization
        if manager.platform == 'ios-ish':
            from ios.ish_utils import ios_init
            if not ios_init():
                print(f"{Colors.RED}[!] iOS initialization failed!{Colors.RESET}")
        
        while True:
            print(f"\n{Colors.ORANGE}Main Menu:{Colors.RESET}")
            print("1. List available attacks")
            print("2. Start attack")
            print("3. Stop attack")
            print("4. Status")
            print("5. Scan network (ARP/Ping)")
            print("6. Scan Wi-Fi networks")
            print("7. Exit")
            
            choice = input(f"{Colors.CYAN}> {Colors.RESET}")
            
            try:
                if choice == "1":
                    manager.list_attacks()
                    
                elif choice == "2":
                    attack = input("Attack name: ")
                    target = input("Target: ")
                    try:
                        power = int(input("Power [1-5]: ") or 1)
                        duration = int(input("Duration (sec): ") or 60)
                    except ValueError:
                        print(f"{Colors.RED}[-] Invalid number{Colors.RESET}")
                        continue
                    
                    manager.start_attack(attack, target, power, duration)
                    
                elif choice == "3":
                    attack = input("Attack name to stop: ")
                    manager.stop_attack(attack)
                    
                elif choice == "4":
                    manager.status()
                    
                elif choice == "5":
                    subnet = input("Subnet [192.168.1.0/24]: ") or "192.168.1.0/24"
                    manager.scan_network(subnet)
                    
                elif choice == "6":
                    manager.scan_wifi_networks()
                    
                elif choice == "7":
                    manager.stop_all_attacks()
                    print(f"{Colors.GREEN}[+] Exiting...{Colors.RESET}")
                    break
                    
                else:
                    print(f"{Colors.RED}[-] Invalid choice{Colors.RESET}")
            
            except Exception as e:
                print(f"{Colors.RED}[-] Error: {str(e)}{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Interrupted by user{Colors.RESET}")
        sys.exit(1)