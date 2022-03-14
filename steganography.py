# LSB BASED IMAGE STEGANOGRAPHY
import os
import PIL
from PIL import Image
from crypto import Crypto

def convertToBinary(message):
    if type(message) == str:
        return ''.join([format(ord(i), '08b') for i in message])
    elif type(message) == bytes:
        return ''.join([format(i, '08b') for i in message])
    elif type(message) == int:
        return format(message, '08b')
    elif type(message) == tuple:
        return [format(i, '08b') for i in message]
    else:
        raise TypeError("Wrong input type")

def convertBinToString(message):
    message = [message[i : i+8] for i in range(0, len(message), 8)]
    return ''.join([chr(int(i, 2)) for i in message])

class ImageSteg:

    def __init__(self, filepath):
        self.delimeter = "c3p0"
        self.filepath = filepath
        self.filename = os.path.split(filepath)[1]
        self.dest_filename = "enc" + self.filename
        self.head = os.path.split(filepath)[0]
        self.image = None
        self.loadImageFromPath()

    def getImage(self):
        return self.image

    def loadImageFromPath(self):
        try:
            self.image = Image.open(self.filepath)
        except (IOError, FileNotFoundError, PIL.UnidentifiedImageError, ValueError, TypeError):
            exit(1)

    def unloadImage(self):
        self.image.close()

    def encryptImage(self, password, PT):
        
        crypto = Crypto(password)
        CT = crypto.encryptPT(PT)
        CT += bytes(self.delimeter, 'utf-8')

        CTbin = convertToBinary(CT)
        print(CTbin)
        if(len(CTbin) > self.image.size[0]*self.image.size[1]):
            raise ValueError("Image too small to encode data")

        idx = 0
        
        for pixelno, pixel in enumerate(self.image.getdata()):
            
            x, y = pixelno%self.image.size[0], pixelno//self.image.size[0]
            r, g, b = convertToBinary(pixel)
            
            if(idx >= len(CTbin)): break;
            if(idx < len(CTbin)):
                r = int(r[:-1] + CTbin[idx], 2)
                idx += 1
            if(idx < len(CTbin)):
                g = int(g[:-1] + CTbin[idx], 2)
                idx += 1
            if(idx < len(CTbin)):
                b = int(b[:-1] + CTbin[idx], 2)
                idx += 1
            
            r = r if type(r) == int else int(r, 2)
            g = g if type(g) == int else int(g, 2)
            b = b if type(b) == int else int(b, 2)
            
            self.image.putpixel((x,y), (r, g, b))

        print("Message hidden!")
        return  self.saveImage()

    def decryptImage(self, password):

        extractedCT = ""
        binDelim = convertToBinary(self.delimeter)

        for pixel in self.image.getdata():
            r, g, b = convertToBinary(pixel)
            extractedCT += r[-1]
            if(extractedCT[-len(binDelim):] == binDelim):
                print("Extracted")
                break
            extractedCT += g[-1]
            if(extractedCT[-len(binDelim):] == binDelim):
                print("Extracted")
                break
            extractedCT += b[-1]
            if(extractedCT[-len(binDelim):] == binDelim):
                print("Extracted")
                break
            
        extractedCT = convertBinToString(extractedCT)
        extractedCT = extractedCT[:extractedCT.find(self.delimeter)]
        crypto = Crypto(password)
        PT = crypto.decryptCT(extractedCT)
        return PT

    def saveImage(self):
        dest_filename_without_suffix, _ = os.path.splitext(self.dest_filename)
        dest_img_path = self.head + dest_filename_without_suffix + ".png"
        self.image.save(dest_img_path, "PNG")
        print("Output file name: ", dest_img_path)
        return dest_img_path
