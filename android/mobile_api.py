import os
import sys
import threading
import time
from flask import Flask, jsonify, request
from core.attack_manager import AttackManager
from core.utils import Colors, print_banner

# Настройки API
API_PORT = 8080
API_HOST = "0.0.0.0"  # Доступ с других устройств

app = Flask(__name__)
manager = AttackManager()

# Ограничение доступа по паролю (базовый уровень безопасности)
API_PASSWORD = "cyberflood123"

def authenticate():
    """Проверка аутентификации через заголовок или параметр"""
    password = request.headers.get('X-API-KEY') or request.args.get('apikey')
    return password == API_PASSWORD

@app.before_request
def require_auth():
    """Требует аутентификацию для всех запросов"""
    if request.endpoint != 'status' and not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

@app.route('/')
def index():
    """Главная страница API"""
    return jsonify({
        "status": "running",
        "project": "CyberFlood Pro",
        "version": "1.0",
        "platform": "android",
        "endpoints": {
            "/attacks": "GET - List available attacks",
            "/attack/start": "POST - Start attack",
            "/attack/stop": "POST - Stop attack",
            "/status": "GET - Current status"
        }
    })

@app.route('/attacks', methods=['GET'])
def list_attacks():
    """Возвращает список доступных атак"""
    return jsonify({"attacks": list(manager.attacks.keys())})

@app.route('/attack/start', methods=['POST'])
def start_attack():
    """Запускает атаку"""
    data = request.json
    required = ['attack', 'target']
    
    if not data or not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400
        
    attack = data['attack']
    target = data['target']
    power = data.get('power', 1)
    duration = data.get('duration', 300)  # 5 минут по умолчанию
    
    # Проверка, что атака существует
    if attack not in manager.attacks:
        return jsonify({"error": f"Attack '{attack}' not available"}), 400
    
    # Запуск атаки в отдельном потоке
    def run_attack():
        manager.start_attack(attack, target, power, duration)
        
    thread = threading.Thread(target=run_attack, daemon=True)
    thread.start()
    
    return jsonify({
        "status": "started",
        "attack": attack,
        "target": target,
        "power": power,
        "duration": duration
    })

@app.route('/attack/stop', methods=['POST'])
def stop_attack():
    """Останавливает атаку"""
    data = request.json
    if not data or 'attack' not in data:
        return jsonify({"error": "Missing attack name"}), 400
        
    attack = data['attack']
    
    if attack not in manager.active_attacks:
        return jsonify({"error": f"No active attack: {attack}"}), 400
        
    manager.stop_attack(attack)
    return jsonify({"status": "stopped", "attack": attack})

@app.route('/status', methods=['GET'])
def status():
    """Возвращает статус системы и активных атак"""
    active_attacks = []
    
    for name, data in manager.active_attacks.items():
        active_attacks.append({
            "name": name,
            "target": data["target"],
            "power": data["power"],
            "elapsed": time.time() - data["start_time"]
        })
    
    return jsonify({
        "status": "online",
        "active_attacks": active_attacks,
        "cpu_usage": os.getloadavg()[0],
        "memory": os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024. ** 2)
    })

def run_mobile_api():
    """Запускает мобильный API сервер"""
    print(f"{Colors.CYAN}[*] Starting Mobile API on {API_HOST}:{API_PORT}{Colors.RESET}")
    print(f"{Colors.YELLOW}[!] API Key: {API_PASSWORD}{Colors.RESET}")
    app.run(host=API_HOST, port=API_PORT, threaded=True)

if __name__ == '__main__':
    # Печать баннера
    print_banner()
    
    # Запуск API в отдельном потоке
    api_thread = threading.Thread(target=run_mobile_api, daemon=True)
    api_thread.start()
    
    # Запуск основного менеджера
    try:
        from core.attack_manager import main
        main()
    except KeyboardInterrupt:
        print(f"{Colors.RED}[!] Shutting down...{Colors.RESET}")
        sys.exit(0)