import argparse
from steganography import ImageSteg

def initParser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--Image", help = "Cover Image path", required=True)
    parser.add_argument("-m", "--MessageImage", help="Message image")
    parser.add_argument("-p", "--PlainText", help = "Plain text to encode", type = str)
    parser.add_argument("-e", "--encrypt", help = "Password/Key for encryption", type = str)
    parser.add_argument("-d", "--decrypt", help = "Password/Key for decryption", type = str)
    parser.add_argument("-t", "--type", help="Text embedding or image embedding: t/i", type=str)
    parser.add_argument("-mo", "--MODE", help="Mode of embeddeing, normal/dct", type=str)
    return parser

if __name__ == '__main__':
    
    parser = initParser()
    args = parser.parse_args()
    if (not args.decrypt and not args.encrypt):
        print("Wrong input")
        exit(1)
    if args.type in ['t', 'text', 'T', 'TEXT']:
        steg = ImageSteg(args.Image)
        if(args.decrypt):    
            PT = steg.decryptImage(args.decrypt)    
            print(PT)
        elif (args.encrypt and args.PlainText):
            path = steg.encryptImage(args.encrypt, args.PlainText)
            print(path)
    else:
        if args.decrypt:   
            steg = ImageSteg(args.Image)
            if args.MODE in ["normal", "n"]:
                PT = steg.decryptImageFromImage(args.decrypt)
            else:
                PT = steg.decryptImageUsingDCT(args.decrypt)
            
        elif (args.encrypt and args.MessageImage):
            steg = ImageSteg(args.Image, args.MessageImage)
            if args.MODE in ["normal", "n"]:
                path = steg.embedImageOntoImage(args.encrypt)
            else:
                path = steg.embedImageUsingDCT(args.encrypt)
            
