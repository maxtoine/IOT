import struct
from interface.interface_cryptage import InterfaceCryptage

class Cryptage(InterfaceCryptage):
    
    ## Clé de 128 bits (4 entiers de 32 bits)
    XTEA_KEY = [0xACE1ACE1, 0x12345678, 0xDEADBEEF, 0xBEEFFACE] 
    ROUNDS = 32
    
    ##  déchiffrement de la trame reçue du micro:bit vers le serveur ( partie mathematiques du XTEA)
    def _xtea_decrypt_block(self, v0: int, v1: int, k: list) -> tuple:
        """Déchiffre un bloc de 64 bits (deux entiers de 32 bits)"""
        v0 = v0 & 0xFFFFFFFF
        v1 = v1 & 0xFFFFFFFF
        delta = 0x9E3779B9
        sum_val = (delta * self.ROUNDS) & 0xFFFFFFFF
        
        for _ in range(self.ROUNDS):
            term1 = ((((v0 << 4) & 0xFFFFFFFF) ^ (v0 >> 5)) + v0) & 0xFFFFFFFF
            term2 = (sum_val + k[(sum_val >> 11) & 3]) & 0xFFFFFFFF
            v1 = (v1 - (term1 ^ term2)) & 0xFFFFFFFF
            
            sum_val = (sum_val - delta) & 0xFFFFFFFF
            
            term3 = ((((v1 << 4) & 0xFFFFFFFF) ^ (v1 >> 5)) + v1) & 0xFFFFFFFF
            term4 = (sum_val + k[sum_val & 3]) & 0xFFFFFFFF
            v0 = (v0 - (term3 ^ term4)) & 0xFFFFFFFF
            
        return v0, v1
    

    ##  chiffrement de la trame vers le micro:bit ( partie mathematiques du XTEA)
    def _xtea_encrypt_block(self, v0: int, v1: int, k: list) -> tuple:
        """Chiffre un bloc de 64 bits (deux entiers de 32 bits)"""
        v0 = v0 & 0xFFFFFFFF
        v1 = v1 & 0xFFFFFFFF
        sum_val = 0
        delta = 0x9E3779B9
        
        for _ in range(self.ROUNDS):
            term1 = ((((v1 << 4) & 0xFFFFFFFF) ^ (v1 >> 5)) + v1) & 0xFFFFFFFF
            term2 = (sum_val + k[sum_val & 3]) & 0xFFFFFFFF
            v0 = (v0 + (term1 ^ term2)) & 0xFFFFFFFF
            
            sum_val = (sum_val + delta) & 0xFFFFFFFF
            
            term3 = ((((v0 << 4) & 0xFFFFFFFF) ^ (v0 >> 5)) + v0) & 0xFFFFFFFF
            term4 = (sum_val + k[(sum_val >> 11) & 3]) & 0xFFFFFFFF
            v1 = (v1 + (term3 ^ term4)) & 0xFFFFFFFF
            
        return v0, v1

    ## fonction qui appelle le chiffrement pour les données à envoyer au micro:bit 
    def decryptage(self, data: bytes) -> bytes:
        # 1. On détermine combien d'entiers de 32 bits (4 octets) il y a dans les bytes
        num_ints = len(data) // 4
        fmt = f'<{num_ints}I' # Format : ex: '<6I' pour 24 octets
        
        # 2. On transforme les bytes en liste d'entiers
        uints = list(struct.unpack(fmt, data))
        
        # 3. On déchiffre par paires
        decrypted_uints = []
        for i in range(0, len(uints), 2):
            v0, v1 = self._xtea_decrypt_block(uints[i], uints[i+1], self.XTEA_KEY)
            decrypted_uints.extend([v0, v1])
            
        # 4. On retransforme les entiers déchiffrés en bytes purs
        return struct.pack(fmt, *decrypted_uints)

    ## fonction qui appelle le chiffrement pour les données à envoyer au micro:bit
    def encryptage(self, data: bytes) -> bytes:
        # Même logique que le déchiffrement, mais dans l'autre sens
        num_ints = len(data) // 4
        fmt = f'<{num_ints}I'
        
        uints = list(struct.unpack(fmt, data))
        
        encrypted_uints = []
        for i in range(0, len(uints), 2):
            v0, v1 = self._xtea_encrypt_block(uints[i], uints[i+1], self.XTEA_KEY)
            encrypted_uints.extend([v0, v1])
            
        return struct.pack(fmt, *encrypted_uints)