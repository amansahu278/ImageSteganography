import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as PBK

def convertToBytes(ip):
    if(type(ip) is bytes): return ip;
    return bytes(ip, 'utf-8')

class Crypto:

    def __init__(self, _password):
        self.salt = b""
        self.password = convertToBytes(_password)
        self.iterations = 390000
        self.length = 32
        self.createKDF()
        self.createKey()

    def createKDF(self):
        self.kdf = PBK(algorithm=hashes.SHA256, salt=self.salt, length=self.length, iterations=self.iterations)
    
    def createKey(self):
        self.key = base64.urlsafe_b64encode(self.kdf.derive(self.password))

    # def encryptFile(self, filepath):
    #     with open(filepath) as fileReader:
    #         PT = fileReader.read()
    #     return self.encryptPT(PT)
    
    # def writeToDecryptFile(self, filepath, CT):
    #     with open(filepath, 'w') as filewriter:
    #         filewriter.write(CT)

    def encryptPT(self, PT):
        fernet = Fernet(self.key)
        CT = fernet.encrypt(convertToBytes(PT))
        return CT
    
    def decryptCT(self, CT):
        fernet = Fernet(self.key)
        PT = fernet.decrypt(convertToBytes(CT))
        return PT.decode('utf-8')
