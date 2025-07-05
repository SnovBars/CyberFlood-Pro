document.addEventListener('DOMContentLoaded', () => {
    // Конфигурация
    const API_URL = 'http://localhost:5000'; // Адрес API сервера
    const API_KEY = 'cyberflood123'; // Ключ API
    const UPDATE_INTERVAL = 3000; // Интервал обновления (мс)
    
    // Элементы DOM
    const startButton = document.getElementById('start-attack');
    const stopButton = document.getElementById('stop-all');
    const attacksList = document.getElementById('attacks-list');
    const cpuLoad = document.getElementById('cpu-load');
    const memUsage = document.getElementById('mem-usage');
    const powerButtons = document.querySelectorAll('.power-selector button');
    
    // Переменные состояния
    let activePower = 3;
    let updateInterval;
    let trafficChart, cpuChart;
    
    // Инициализация
    initPowerSelector();
    initCharts();
    startUpdater();
    
    // Обработчики событий
    startButton.addEventListener('click', startAttack);
    stopButton.addEventListener('click', stopAllAttacks);
    
    // Инициализация выбора мощности
    function initPowerSelector() {
        powerButtons.forEach(button => {
            button.addEventListener('click', () => {
                powerButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                activePower = parseInt(button.dataset.power);
            });
        });
    }
    
    // Инициализация графиков
    function initCharts() {
        const ctx1 = document.getElementById('traffic-chart').getContext('2d');
        trafficChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [{
                    label: 'Outgoing Traffic (Mbps)',
                    data: Array(20).fill(0),
                    borderColor: '#6a0dad',
                    backgroundColor: 'rgba(106, 13, 173, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#252536' } },
                    x: { display: false, grid: { display: false } }
                }
            }
        });
        
        const ctx2 = document.getElementById('cpu-chart').getContext('2d');
        cpuChart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: Array(10).fill(''),
                datasets: [{
                    label: 'CPU Load',
                    data: Array(10).fill(0),
                    backgroundColor: '#ff6b00',
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, max: 100, grid: { color: '#252536' } },
                    x: { display: false, grid: { display: false } }
                }
            }
        });
    }
    
    // Запуск атаки
    async function startAttack() {
        const attackType = document.getElementById('attack-type').value;
        const target = document.getElementById('target').value.trim();
        const duration = document.getElementById('duration').value;
        
        if (!target) {
            alert('Please enter a target');
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/attack/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': API_KEY
                },
                body: JSON.stringify({
                    attack: attackType,
                    target: target,
                    power: activePower,
                    duration: duration
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'started') {
                showNotification(`Attack started: ${attackType} → ${target}`, 'success');
            } else {
                showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            showNotification('Connection error: ' + error.message, 'error');
        }
    }
    
    // Остановка всех атак
    async function stopAllAttacks() {
        try {
            // Получаем список активных атак
            const statusResponse = await fetch(`${API_URL}/status`);
            const status = await statusResponse.json();
            
            // Останавливаем каждую атаку
            for (const attackName in status.active_attacks) {
                await fetch(`${API_URL}/attack/stop`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-KEY': API_KEY
                    },
                    body: JSON.stringify({ attack: attackName })
                });
            }
            
            showNotification('All attacks stopped', 'success');
        } catch (error) {
            showNotification('Error stopping attacks: ' + error.message, 'error');
        }
    }
    
    // Обновление интерфейса
    async function updateInterface() {
        try {
            // Получение статуса системы
            const statusResponse = await fetch(`${API_URL}/status`);
            const status = await statusResponse.json();
            
            // Обновление системных показателей
            cpuLoad.textContent = Math.round(status.cpu_usage * 100) + '%';
            memUsage.textContent = Math.round(status.memory) + 'MB';
            
            // Обновление списка атак
            updateAttacksList(status.active_attacks);
            
            // Обновление графиков
            updateCharts(status);
        } catch (error) {
            console.error('Update error:', error);
        }
    }
    
    // Обновление списка атак
    function updateAttacksList(attacks) {
        if (Object.keys(attacks).length === 0) {
            attacksList.innerHTML = '<div class="empty">No active attacks</div>';
            return;
        }
        
        attacksList.innerHTML = '';
        
        for (const [name, info] of Object.entries(attacks)) {
            const elapsed = Math.floor(info.elapsed);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            const attackElement = document.createElement('div');
            attackElement.className = 'attack-item';
            attackElement.innerHTML = `
                <div class="attack-info">
                    <div class="attack-type">${name.replace(/_/g, ' ').toUpperCase()}</div>
                    <div class="attack-target">${info.target}</div>
                </div>
                <div class="attack-stats">
                    <div class="stat power">POWER: ${info.power}</div>
                    <div class="stat time">${minutes}m ${seconds}s</div>
                </div>
                <div class="attack-controls">
                    <button class="btn-stop" data-attack="${name}">
                        <i class="fas fa-stop"></i>
                    </button>
                </div>
            `;
            
            attacksList.appendChild(attackElement);
        }
        
        // Добавление обработчиков для кнопок остановки
        document.querySelectorAll('.attack-controls .btn-stop').forEach(button => {
            button.addEventListener('click', async () => {
                const attackName = button.dataset.attack;
                await stopAttack(attackName);
            });
        });
    }
    
    // Остановка конкретной атаки
    async function stopAttack(attackName) {
        try {
            await fetch(`${API_URL}/attack/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': API_KEY
                },
                body: JSON.stringify({ attack: attackName })
            });
            
            showNotification(`Attack stopped: ${attackName}`, 'success');
        } catch (error) {
            showNotification(`Error stopping attack: ${error.message}`, 'error');
        }
    }
    
    // Обновление графиков
    function updateCharts(status) {
        // Traffic Chart
        const trafficData = trafficChart.data.datasets[0].data;
        const newTraffic = Math.random() * 100; // В реальности получаем с сервера
        trafficData.push(newTraffic);
        trafficData.shift();
        trafficChart.update();
        
        // CPU Chart
        const cpuData = cpuChart.data.datasets[0].data;
        const cpuValue = status.cpu_usage * 100;
        cpuData.push(cpuValue);
        cpuData.shift();
        cpuChart.update();
    }
    
    // Запуск периодического обновления
    function startUpdater() {
        updateInterface();
        updateInterval = setInterval(updateInterface, UPDATE_INTERVAL);
    }
    
    // Показать уведомление
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // Добавление стилей для уведомлений
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .notification.show {
            opacity: 1;
            transform: translateX(0);
        }
        
        .notification.success {
            background: #00c853;
            box-shadow: 0 5px 15px rgba(0, 200, 83, 0.3);
        }
        
        .notification.error {
            background: #ff3d3d;
            box-shadow: 0 5px 15px rgba(255, 61, 61, 0.3);
        }
    `;
    document.head.appendChild(style);
});