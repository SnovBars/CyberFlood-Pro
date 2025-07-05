import os
import platform
import sys
import time

class Colors:
    """ANSI escape codes for terminal colors"""
    RED = "\033[38;2;255;0;0m"
    GREEN = "\033[38;2;0;255;0m"
    YELLOW = "\033[38;2;255;255;0m"
    ORANGE = "\033[38;2;255;165;0m"
    BLUE = "\033[38;2;0;120;255m"
    PURPLE = "\033[38;2;128;0;128m"
    CYAN = "\033[38;2;0;255;255m"
    MAGENTA = "\033[38;2;255;0;255m"
    WHITE = "\033[38;2;255;255;255m"
    RESET = "\033[0m"
    
    @staticmethod
    def gradient_text(text, start_color, end_color):
        """Создает градиентный текст"""
        try:
            r1, g1, b1 = start_color
            r2, g2, b2 = end_color
            gradient = ""
            length = len(text)
            
            for i, char in enumerate(text):
                r = int(r1 + (r2 - r1) * i / length)
                g = int(g1 + (g2 - g1) * i / length)
                b = int(b1 + (b2 - b1) * i / length)
                gradient += f"\033[38;2;{r};{g};{b}m{char}"
                
            return gradient + Colors.RESET
        except:
            return text

def detect_platform():
    """Определяет текущую платформу"""
    if 'ANDROID_ARGUMENT' in os.environ:
        return 'android'
    elif 'termux' in os.environ.get('PREFIX', ''):
        return 'termux'
    elif 'ish' in platform.platform().lower():
        return 'ios-ish'
    elif platform.system() == 'Linux':
        return 'linux'
    elif platform.system() == 'Windows':
        return 'windows'
    elif platform.system() == 'Darwin':
        return 'macos'
    return 'unknown'

def print_banner():
    """Выводит ASCII-баннер с градиентом"""
    banner = r"""
     ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██████╗ ██╗      ██████╗  ██████╗ ██████╗ 
    ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔══██╗
    ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██████╔╝██║     ██║   ██║██║   ██║██║  ██║
    ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██╗██║     ██║   ██║██║   ██║██║  ██║
    ╚██████╗   ██║   ██║  ██║███████╗██║  ██║██║  ██║███████╗╚██████╔╝╚██████╔╝██████╔╝
     ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ 
    """
    
    # Градиент от фиолетового (106,13,173) к красному (255,0,0)
    lines = banner.strip().split('\n')
    start_color = (106, 13, 173)
    end_color = (255, 0, 0)
    
    for line in lines:
        print(Colors.gradient_text(line, start_color, end_color))
    
    subtitle = "═══════ Layer 4/7 Hybrid DDoS Framework ═══════"
    print(Colors.gradient_text(subtitle, (255, 0, 0), (255, 165, 0)))
    print(f"{Colors.CYAN}Version: 1.0 | Platform: {detect_platform()}{Colors.RESET}")
    print(f"{Colors.RED}WARNING: For educational purposes only!{Colors.RESET}\n")

def clear_screen():
    """Очищает экран терминала"""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def progress_bar(duration, stop_event):
    """Отображает прогресс-бар"""
    start_time = time.time()
    bar_length = 40
    
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1.0)
        filled = int(bar_length * progress)
        bar = '█' * filled + '-' * (bar_length - filled)
        
        # Расчет цвета: от зеленого к красному
        r = int(255 * progress)
        g = int(255 * (1 - progress))
        color_code = f"\033[38;2;{r};{g};0m"
        
        print(f"\r{color_code}[{bar}] {int(progress*100)}%", end="")
        
        if progress >= 1.0:
            break
            
        time.sleep(0.1)
    
    print(Colors.RESET)