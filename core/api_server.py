from flask import Flask, jsonify, request
from .attack_manager import AttackManager
from .utils import Colors
import threading

app = Flask(__name__)
manager = AttackManager()

# Простой "бановый" список для безопасности
ALLOWED_IPS = ['127.0.0.1', '192.168.1.0/24']

@app.before_request
def limit_remote_addr():
    """Ограничивает доступ по IP"""
    client_ip = request.remote_addr
    allowed = False
    
    for ip in ALLOWED_IPS:
        if '/' in ip:
            # Проверка CIDR
            network, mask = ip.split('/')
            mask = int(mask)
            # Упрощенная проверка CIDR (для демо)
            if client_ip.startswith(network.rsplit('.', 1)[0]):
                allowed = True
                break
        elif client_ip == ip:
            allowed = True
            break
            
    if not allowed:
        return jsonify({"error": "Access denied"}), 403

@app.route('/attacks', methods=['GET'])
def list_attacks():
    """Возвращает список доступных атак"""
    return jsonify({"attacks": list(manager.attacks.keys())})

@app.route('/attack/start', methods=['POST'])
def start_attack():
    """Запускает атаку"""
    data = request.json
    required = ['attack', 'target']
    
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400
        
    attack = data['attack']
    target = data['target']
    power = data.get('power', 1)
    duration = data.get('duration', 60)
    
    success = manager.start_attack(attack, target, power, duration)
    
    if success:
        return jsonify({"status": "started", "attack": attack, "target": target})
    else:
        return jsonify({"error": "Failed to start attack"}), 500

@app.route('/attack/stop', methods=['POST'])
def stop_attack():
    """Останавливает атаку"""
    data = request.json
    if 'attack' not in data:
        return jsonify({"error": "Missing attack name"}), 400
        
    success = manager.stop_attack(data['attack'])
    
    if success:
        return jsonify({"status": "stopped", "attack": data['attack']})
    else:
        return jsonify({"error": "Failed to stop attack"}), 500

@app.route('/status', methods=['GET'])
def status():
    """Возвращает статус активных атак"""
    active = {}
    for name, data in manager.active_attacks.items():
        active[name] = {
            "target": data["target"],
            "power": data["power"],
            "elapsed": time.time() - data["start_time"]
        }
        
    return jsonify({"active_attacks": active})

def run_api_server():
    """Запускает API сервер в отдельном потоке"""
    print(f"{Colors.CYAN}[*] Starting API server on 127.0.0.1:5000{Colors.RESET}")
    app.run(host='127.0.0.1', port=5000, threaded=True)

if __name__ == '__main__':
    # Запуск в отдельном потоке
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Запуск основного менеджера
    from attack_manager import main
    main()