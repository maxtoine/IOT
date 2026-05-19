#include "MicroBit.h"

MicroBit uBit;

// Relais Radio -> PC (Série)
void onRadioReceived(MicroBitEvent) {
    PacketBuffer b = uBit.radio.datagram.recv();
    if (b.length() > 0) {
        // On envoie les octets bruts reçus de la radio vers le PC via le port série
        uBit.serial.send(b.getBytes(), b.length());
    }
}

int main() {
    uBit.init();
    uBit.radio.setGroup(52);
    uBit.radio.enable();
    
    // Taille des buffers augmentée pour éviter de perdre des octets
    uBit.serial.setRxBufferSize(64);
    uBit.serial.setTxBufferSize(64);
    uBit.serial.baud(115200);

    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onRadioReceived);

    while(1) {
        // Relais PC (Série) -> Radio
        // On attend d'avoir reçu exactement 32 octets
        if (uBit.serial.rxBufferedSize() >= 32) {
            
            uint8_t buffer[32]; 
            
            // Lecture de 32 octets bruts depuis le port série
            int bytesRead = uBit.serial.read(buffer, 32); 

            if (bytesRead == 32) {
                // VÉRIFICATION DE L'OCTET DE FIN
                // Si le 32ème octet (index 31) est bien 255, la trame est valide
                if (buffer[31] == 255) {
                    uBit.radio.datagram.send(buffer, 32); 
                } 
                else {
                    // Si ce n'est pas 255, la trame est décalée ou corrompue.
                    // On l'ignore simplement pour éviter d'envoyer des déchets à la radio.
                  
                }
            }
        }

        uBit.sleep(50);
    }
}