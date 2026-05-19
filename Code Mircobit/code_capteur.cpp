#include "MicroBit.h"
#include "ssd1306.h"
#include "bme280.h"
#include "veml6070.h"
#include "tsl256x.h"

// Structure binaire de 25 octets pour serveur_2.py
struct __attribute__((packed)) MaTrame {
    uint8_t  adresse_dest; // Identifiant du serveur
    uint8_t  adresse_source; // Identifiant du micro:bit
    char     tag[5]; // 5 caractères pour indiquer l'ordre d'affichage (ex: "TLHPU")
    uint32_t payload[6];// 6 valeurs de capteurs (T, L, H, P, U + 1 pour le padding)
    uint8_t  fin; // Caractère de fin de trame
};
MicroBit uBit;
MicroBitI2C i2c(MICROBIT_PIN_P20, MICROBIT_PIN_P19);
MicroBitPin P0(MICROBIT_ID_IO_P0, MICROBIT_PIN_P0, PIN_CAPABILITY_DIGITAL_OUT);

int adresse_passerelle = 00; // Identifiant de la passerelle (pour le micro:bit)
int adresse_microbit = 42; // Identifiant du micro:bit (pour la passerelle)

// Variables globales pour l'affichage dynamique 
ManagedString currentOrder = "TLHPU"; 
float valT = 0, valL = 0, valH = 0, valP = 0, valU = 0;

// Clé de chiffrement 128 bits (16 octets)
uint32_t key[4] = {0xACE1ACE1, 0x12345678, 0xDEADBEEF, 0xBEEFFACE};

// Fonction de chiffrement XTEA (32 rounds) pour sécuriser les données envoyées à la passerelle
//
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
// Écouter la passerelle pour la configuration d'affichage 
void onConfigurationReceived(MicroBitEvent) {
    PacketBuffer buffer = uBit.radio.datagram.recv();
    
    // On s'assure que le paquet reçu a bien la taille exacte de notre structure (25 octets)
    if (buffer.length() == sizeof(MaTrame)) {
        
        // On "cast" (plaque) les données brutes reçues directement dans le format MaTrame
        MaTrame* trameRecue = (MaTrame*)buffer.getBytes();
        
        // On vérifie si l'identifiant de destination correspond à notre micro:bit (42)
        if (trameRecue->adresse_dest == adresse_microbit) {
            
            // Si c'est pour nous, on extrait les 5 caractères du tag
            char nouveauTag[6] = {0}; // Tableau de 6 pour inclure la fin de chaîne '\0' obligatoire pour ManagedString
            memcpy(nouveauTag, trameRecue->tag, 5);
            
            currentOrder = ManagedString(nouveauTag); // Mise à jour de l'ordre (ex: "LTHPU")
        }
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
    trame.adresse_dest = adresse_passerelle; // Identifiant de la passerelle
    trame.adresse_source = adresse_microbit; // Identifiant du micro:bit
    memcpy(trame.tag, (char*)currentOrder.toCharArray(), 5); // On copie les 5 caractères de l'ordre dans le champ tag (ex: "TLHPU")
    trame.fin = 255;// Octet de fin fixe pour valider la trame côté passerelle

    while(1) {
        // 1. initialisation des variables pour les données capteurs
        uint32_t rawP = 0; int32_t rawT = 0; uint16_t rawH = 0;        
        bme.sensor_read(&rawP, &rawT, &rawH);

        // Conversion des données brutes en valeurs exploitables (float) selon les formules de compensation du BME280
        valT = (float)(bme.compensate_temperature(rawT) / 100.0);
        valP = (float)(bme.compensate_pressure(rawP) / 100.0);
        valH = (float)(bme.compensate_humidity(rawH) / 1024.0);
        
        uint16_t c = 0, ir = 0; uint32_t lux = 0;        
        tsl.sensor_read(&c, &ir, &lux);
        valL = (float)lux;

        uint16_t uv = 0;
        veml.sensor_read(&uv);
        valU = (float)uv;

        // 2. On prépare les données claires
        float data_claire[6] = {valT, valL, valH, valP, valU, 0.0f}; 

        // 3.  On copie dans un tableau temporaire (buffer) pour le chiffrement
        uint32_t payload_buffer[6]; 
        memcpy(payload_buffer, data_claire, 24);

        // 4. On chiffre le buffer de travail en 3 blocs de 8 octets (2 uint32_t) avec XTEA
        for(int i=0; i<3; i++) {
            xtea_encrypt(32, &payload_buffer[i*2], key);
        }

        // 5. On place le buffer chiffré dans la trame finale
        memcpy(trame.payload, payload_buffer, 24); 
        
        // Envoyer les informations à la passerelle via Radio 
        uBit.radio.datagram.send((uint8_t*)&trame, sizeof(MaTrame));

        //  Mise à jour de l'affichage OLED selon l'ordre en vigueur 
        mettreAJourOLED(screen);

        uBit.sleep(2000);
    }
}