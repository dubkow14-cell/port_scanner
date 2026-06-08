#!/usr/bin/env python3
import socket
import sys
import threading
from datetime import datetime
from queue import Queue

# Цвета для вывода (делают терминал красивее)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

# Словарь известных портов и их сервисов
KNOWN_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    111: "RPC",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
    27017: "MongoDB",
}

def get_service_name(port):
    """Возвращает название сервиса для порта"""
    return KNOWN_PORTS.get(port, "Unknown")

def scan_port(host, port, results):
    """Сканирует один порт"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            service = get_service_name(port)
            results[port] = service
            print(f"{Colors.GREEN}[+] Port {port} is OPEN{Colors.RESET} → {Colors.YELLOW}{service}{Colors.RESET}")
    except:
        pass

def worker(host, results, q):
    """Функция для потока-воркера"""
    while True:
        port = q.get()
        scan_port(host, port, results)
        q.task_done()

def scan_host(host, threads=100):
    """Многопоточное сканирование портов"""
    print(f"{Colors.BLUE}[*] Starting scan on {host}{Colors.RESET}")
    print(f"[*] Start time: {datetime.now()}")
    print(f"[*] Using {threads} threads\n")
    
    results = {}
    q = Queue()
    
    # Заполняем очередь портами
    for port in range(1, 1025):
        q.put(port)
    
    # Запускаем потоки
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(host, results, q))
        t.daemon = True
        t.start()
    
    # Ждём завершения
    q.join()
    
    # Статистика
    print(f"\n{Colors.BLUE}[*] Scan completed!{Colors.RESET}")
    print(f"[*] End time: {datetime.now()}")
    print(f"[*] Open ports found: {len(results)}")
    
    # Сохраняем в файл
    if results:
        save_results(host, results)
    
    return results

def save_results(host, results):
    """Сохраняет результаты в файл"""
    filename = f"scan_{host.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Scan results for {host}\n")
        f.write(f"Scan time: {datetime.now()}\n")
        f.write(f"Open ports found: {len(results)}\n")
        f.write("-" * 50 + "\n")
        for port, service in sorted(results.items()):
            f.write(f"Port {port}: {service}\n")
    
    print(f"{Colors.GREEN}[+] Results saved to {filename}{Colors.RESET}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <IP or hostname>")
        print(f"Example: {sys.argv[0]} 127.0.0.1")
        print(f"Example: {sys.argv[0]} scanme.nmap.org")
        sys.exit(1)
    
    host = sys.argv[1]
    
    try:
        scan_host(host, threads=100)
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Scan interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {e}{Colors.RESET}")
        sys.exit(1)
