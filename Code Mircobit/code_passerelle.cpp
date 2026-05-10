#include "MicroBit.h"

MicroBit uBit;

//  Relais Radio -> PC (Série)
void onRadioReceived(MicroBitEvent) {
    PacketBuffer b = uBit.radio.datagram.recv();
    if (b.length() > 0) {
        // On envoie les octets bruts au PC
        uBit.serial.send(b.getBytes(), b.length());
    }
}

int main() {
    uBit.init();
    uBit.radio.setGroup(52);
    uBit.radio.enable();
    
    //  taille des buffers augmenté pour éviter de perdre des octets
    uBit.serial.setRxBufferSize(64);
    uBit.serial.setTxBufferSize(64);
    uBit.serial.baud(115200);

    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onRadioReceived);

    while(1) {
        // Relais PC (Série) -> Radio
        // Écoute les ordres envoyés par l'application Android via le serveur Python
        if (uBit.serial.rxBufferedSize() > 0) {
            ManagedString config = uBit.serial.readUntil("\n", ASYNC); 
            if (config.length() > 0) {
                uBit.radio.datagram.send(config); // Transfert de l'ordre au capteur
            }
        }

        uBit.sleep(50);
    }
}