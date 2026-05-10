#include "MicroBit.h"
#include "ssd1306.h"
#include "bme280.h"
#include "veml6070.h"
#include "tsl256x.h"

// Structure binaire de 25 octets pour serveur_2.py
struct __attribute__((packed)) MaTrame {
    uint8_t  adresse; 
    char     tag[4]; 
    uint32_t payload[6];
    uint8_t  fin;
};
MicroBit uBit;
MicroBitI2C i2c(MICROBIT_PIN_P20, MICROBIT_PIN_P19);
MicroBitPin P0(MICROBIT_ID_IO_P0, MICROBIT_PIN_P0, PIN_CAPABILITY_DIGITAL_OUT);

// Variables globales pour l'affichage dynamique 
ManagedString currentOrder = "TLHPU"; 
float valT = 0, valL = 0, valH = 0, valP = 0, valU = 0;

// Clé de chiffrement 128 bits (16 octets)
uint32_t key[4] = {0xACE1ACE1, 0x12345678, 0xDEADBEEF, 0xBEEFFACE};

// Fonction de chiffrement XTEA (32 rounds) pour sécuriser les données envoyées à la passerelle
void xtea_encrypt(uint32_t num_rounds, uint32_t v[2], uint32_t const k[4]) {
    uint32_t v0 = v[0], v1 = v[1], sum = 0, delta = 0x9E3779B9;
    for (uint32_t i = 0; i < num_rounds; i++) {
        v0 += (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + k[sum & 3]);
        sum += delta;
        v1 += (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + k[(sum >> 11) & 3]);
    }
    v[0] = v0; v[1] = v1;
}

// Écouter la passerelle pour la configuration d'affichage 
void onConfigurationReceived(MicroBitEvent) {
    ManagedString s = uBit.radio.datagram.recv();
    if (s.length() > 0) {
        currentOrder = s; // Mise à jour de l'ordre (ex: "LTH")
    }
}
ManagedString formaterCapteur(char c) { // Formate la valeur du capteur selon le type demandé (T, L, H, P, U)
    if (c == 'T') return "T:" + ManagedString((int)valT) + "C";
    if (c == 'L') return "L:" + ManagedString((int)valL) + "lx";
    if (c == 'H') return "H:" + ManagedString((int)valH) + "%";
    if (c == 'P') return "P:" + ManagedString((int)valP) + "hP";
    if (c == 'U') return "U:" + ManagedString((int)valU) + "uv";
    return "";
}
// Fonction d'affichage dynamique sur l'écran OLED (l'Acteur) 
//j'ai decoupé en 4 lignes ( 2 capteurs par lignes) pour que ce soit plus lisible et éviter les problèmes de formatage sur l'écran 128x64
void mettreAJourOLED(ssd1306 &screen) {
    screen.clear(); 
    
    // Construction de la Ligne 0 (ex: "T:25C  L:49lx")
    // On ajoute des espaces entre les deux pour bien séparer
    ManagedString L0 = formaterCapteur(currentOrder.charAt(0)) + " " + 
                       formaterCapteur(currentOrder.charAt(1));
    
    // Construction de la Ligne 1 (ex: "H:3%  P:999hP")
    ManagedString L1 = formaterCapteur(currentOrder.charAt(2)) + " " + 
                       formaterCapteur(currentOrder.charAt(3));

    // Construction de la Ligne 2 (le 5ème capteur tout seul)
    ManagedString L2 = formaterCapteur(currentOrder.charAt(4));

    // Ligne 3 : Debug pour confirmer l'ordre radio
    ManagedString L3 = "ORD: " + currentOrder;

    // Envoi des 4 lignes physiques à l'écran
    screen.display_line(0, 0, (char*)L0.toCharArray());
    screen.display_line(1, 0, (char*)L1.toCharArray());
    screen.display_line(2, 0, (char*)L2.toCharArray());
    screen.display_line(3, 0, (char*)L3.toCharArray());

    screen.update_screen();
}

int main() {
    // Initialisation des capteurs, de l'écran et de la radio
    uBit.init();
    uBit.radio.setGroup(52);
    uBit.radio.enable();
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onConfigurationReceived);

    ssd1306 screen(&uBit, &i2c, &P0, 0x78);
    bme280 bme(&uBit, &i2c);
    tsl256x tsl(&uBit, &i2c);
    veml6070 veml(&uBit, &i2c);

    MaTrame trame;
    trame.adresse = 42; // Identifiant du bureau 
    memcpy(trame.tag, (char*)currentOrder.toCharArray(), 5); // On copie les 5 caractères de l'ordre dans le champ tag (ex: "TLHPU")
    trame.fin = 255;// Octet de fin fixe pour valider la trame côté passerelle

    while(1) {
        // 1. Lecture des capteurs 
        uint32_t rawP; int32_t rawT; uint16_t rawH;
        bme.sensor_read(&rawP, &rawT, &rawH);
        valT = (float)(bme.compensate_temperature(rawT) / 100.0);
        valP = (float)(bme.compensate_pressure(rawP) / 100.0);
        valH = (float)(bme.compensate_humidity(rawH) / 1024.0);
        
        uint16_t c, ir; uint32_t lux;
        tsl.sensor_read(&c, &ir, &lux);
        valL = (float)lux;

        uint16_t uv;
        veml.sensor_read(&uv);
        valU = (float)uv;

        float data_claire[6] = {valT, valL, valH, valP, valU, 0.0f}; // On ajoute un 6ème float à 0 pour compléter les 24 octets de payload (6*4 octets) et éviter les problèmes de formatage côté passerelle   

        uint32_t* p = (uint32_t*)data_claire; // On chiffre les données 2 par 2 (8 octets) pour sécuriser les informations sensibles avant de les envoyer à la passerelle
        for(int i=0; i<3; i++) {
            xtea_encrypt(32, &p[i*2], key);
        }

        memcpy(trame.payload, p, 24);
        
        // Envoyer les informations à la passerelle via Radio 
        uBit.radio.datagram.send((uint8_t*)&trame, sizeof(MaTrame));

        //  Mise à jour de l'affichage OLED selon l'ordre en vigueur 
        mettreAJourOLED(screen);

        uBit.sleep(2000);
    }
}