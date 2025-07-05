import os
import sys
import subprocess
from core.utils import Colors

class iOSUtils:
    """Вспомогательные функции для работы на iOS (iSH)"""
    
    @staticmethod
    def check_root():
        """Проверяет наличие root-прав"""
        if os.geteuid() != 0:
            print(f"{Colors.RED}[!] Root access required! Run with 'sudo'")
            print(f"[!] Enable 'Full iSH Version' for root access{Colors.RESET}")
            return False
        return True
    
    @staticmethod
    def enable_tun_tap():
        """Включает поддержку TUN/TAP (требует root)"""
        if not iOSUtils.check_root():
            return False
            
        try:
            # Создаем TUN устройство
            subprocess.run(["mkdir", "-p", "/dev/net"], check=True)
            subprocess.run(["mknod", "/dev/net/tun", "c", "10", "200"], check=True)
            subprocess.run(["chmod", "0666", "/dev/net/tun"], check=True)
            
            print(f"{Colors.GREEN}[✓] TUN/TAP device created{Colors.RESET}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}[-] Failed to create TUN device: {str(e)}{Colors.RESET}")
            return False
    
    @staticmethod
    def configure_network():
        """Настраивает сетевые параметры для iOS"""
        try:
            # Включаем IP forwarding
            subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)
            
            # Разрешаем RAW сокеты
            subprocess.run(["sysctl", "-w", "net.ipv4.raw_l3_dev_accept=1"], check=True)
            
            print(f"{Colors.GREEN}[✓] Network configured for attacks{Colors.RESET}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}[-] Network config failed: {str(e)}{Colors.RESET}")
            return False
    
    @staticmethod
    def optimize_performance():
        """Оптимизирует производительность для iOS"""
        try:
            # Увеличиваем лимиты файловых дескрипторов
            subprocess.run(["ulimit", "-n", "8192"], check=True)
            
            # Оптимизация параметров сети
            subprocess.run(["sysctl", "-w", "net.core.netdev_max_backlog=5000"], check=True)
            subprocess.run(["sysctl", "-w", "net.core.somaxconn=1024"], check=True)
            
            print(f"{Colors.GREEN}[✓] Performance optimized{Colors.RESET}")
            return True
        except:
            print(f"{Colors.YELLOW}[!] Performance optimization skipped{Colors.RESET}")
            return False
    
    @staticmethod
    def start_ios_service():
        """Запускает необходимые сервисы для iOS"""
        if not iOSUtils.check_root():
            return False
            
        try:
            # Запускаем необходимые сервисы
            subprocess.Popen(["syslogd"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Настраиваем время
            subprocess.run(["ntpd", "-q"], check=True)
            
            print(f"{Colors.GREEN}[✓] Background services started{Colors.RESET}")
            return True
        except:
            print(f"{Colors.YELLOW}[!] Failed to start background services{Colors.RESET}")
            return False

def ios_init():
    """Инициализация окружения для iOS"""
    print(f"{Colors.CYAN}[*] Initializing iOS environment{Colors.RESET}")
    
    # Проверка версии iSH
    if "ish" not in sys.platform:
        print(f"{Colors.RED}[-] Not running in iSH environment{Colors.RESET}")
        return False
    
    # Настройка окружения
    iOSUtils.enable_tun_tap()
    iOSUtils.configure_network()
    iOSUtils.optimize_performance()
    iOSUtils.start_ios_service()
    
    # Проверка важных компонентов
    try:
        subprocess.check_output(["g++", "--version"])
        subprocess.check_output(["python3", "--version"])
        print(f"{Colors.GREEN}[✓] Environment ready{Colors.RESET}")
        return True
    except:
        print(f"{Colors.RED}[-] Essential components missing{Colors.RESET}")
        return False

# Автоматическая инициализация при импорте
if __name__ == "__main__":
    ios_init()