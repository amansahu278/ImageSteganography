import argparse
from steganography import ImageSteg

def initParser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--Image", help = "Cover Image path", required=True)
    parser.add_argument("-p", "--PlainText", help = "Plain text to encode", type = str)
    parser.add_argument("-e", "--encrypt", help = "Password/Key for encryption", type = str)
    parser.add_argument("-d", "--decrypt", help = "Password/Key for decryption", type = str)
    return parser

if __name__ == '__main__':
    
    parser = initParser()
    args = parser.parse_args()
    steg = ImageSteg(args.Image)
    if (not args.decrypt and not args.encrypt):
        print("Wrong input")
        exit(1)
    elif(args.decrypt):
        PT = steg.decryptImage(args.decrypt)    
        print(PT)
    elif (args.encrypt and args.PlainText):
        path = steg.encryptImage(args.encrypt, args.PlainText)
        print(path)
