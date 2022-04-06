# LSB BASED IMAGE STEGANOGRAPHY
from lib2to3.pytree import convert
import os
from io import BytesIO
import base64
import PIL
import numpy as np
from PIL import Image
from crypto import Crypto

def convertToBinary(message):
    if type(message) == str:
        return ''.join([format(ord(i), '08b') for i in message])
    elif type(message) == bytes:
        return ''.join([format(i, '08b') for i in message])
    elif type(message) == int or type(message) == np.uint8:
        return format(message, '08b')
    elif type(message) == tuple:
        return [format(i, '08b') for i in message]
    else:
        raise TypeError("Wrong input type")

def convertBinToString(message):
    message = [message[i : i+8] for i in range(0, len(message), 8)]
    return ''.join([chr(int(i, 2)) for i in message])

class ImageSteg:

    def __init__(self, cover_image_path, message_image_path = None):
        ## TODO: Add input for another file, possibly mode functionality too
        self.delimeter = "c3p0"
        self.blocksize = 8*8
        self.message_image_size_crop = (0, 0, 64, 64)

        self.cover_image_path = cover_image_path
        self.cover_image_filename = os.path.split(self.cover_image_path)[1]
        self.dest_filename = "enc" + self.cover_image_filename
        self.head = os.path.split(self.cover_image_path)[0]
        
        self.cover_image = None
        self.message_image = None
        
        self.message_image_path = message_image_path
        self.loadImagesFromPath()
        self.cropMessageImage()

    def get_bytes_of_image(self, image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        return img_str 

    def get_cover_image(self):
        return self.cover_image

    def loadImagesFromPath(self):
        try:
            self.cover_image = Image.open(self.cover_image_path).convert('RGB')
            self.message_image = Image.open(self.message_image_path).convert('RGB')
        except (IOError, FileNotFoundError, PIL.UnidentifiedImageError, ValueError, TypeError) as e:
            print(e)
            exit(1)

    def cropMessageImage(self):
        self.message_image = self.message_image.crop(self.message_image_size_crop)
        self.message_image.save("cropped_msg.png", 'PNG')

    def unloadImages(self):
        self.cover_image.close()
        self.message_image.close()

    def encryptImage(self, password, PT):
        
        crypto = Crypto(password)
        CT = crypto.encryptPT(PT)
        CT += bytes(self.delimeter, 'utf-8')

        CTbin = convertToBinary(CT)
        print(CTbin)
        if(len(CTbin) > self.cover_image.size[0]*self.cover_image.size[1]):
            raise ValueError("Image too small to encode data")

        idx = 0
        
        for pixelno, pixel in enumerate(self.cover_image.getdata()):
            
            x, y = pixelno%self.cover_image.size[0], pixelno//self.cover_image.size[0]
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
            
            self.cover_image.putpixel((x,y), (r, g, b))

        print("Message hidden!")
        return  self.saveImage()

    def decryptImage(self, password):

        extractedCT = ""
        binDelim = convertToBinary(self.delimeter)

        for pixel in self.cover_image.getdata():
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
        self.unloadImage()
        return PT

    def embedImageOntoImage(self, password):
        cover_image_pixel_no = 0
        w, h = self.cover_image.size
        crypto = Crypto(password)
        CT_chained = bytes()

        for block in range(64):
            column = block % 8 # Block 0->0, 1->1, 2->2, 3->3... 7->7, 8->0, 9->1
            row = block // 8 # Block 0,1,2,3,4,5,6,7->0. 8,9..->1
            
            start = (column * 8, row*8)
            end   = ((column+1)*8, (row+1)*8)
            
            chunk = self.message_image.crop((start[0], start[1], end[0], end[1]))
            chunk_flat = np.asarray(chunk).flatten()
            chunk_flat_bin = [convertToBinary(i) for i in chunk_flat]
            chunk_fin = ''.join(chunk_flat_bin)
            PT_bytes = convertBinToString(chunk_fin)
            CT = crypto.encryptPT(PT_bytes)
            CT_chained += CT
        
        CT_chained += bytes(self.delimeter, 'utf-8')
        CTbin = convertToBinary(CT_chained)
        idx = 0
        while idx < len(CTbin):
            x, y = cover_image_pixel_no%self.cover_image.size[0], cover_image_pixel_no//self.cover_image.size[0]
            pixel = self.cover_image.getpixel((x,y))
            r, g, b = convertToBinary(pixel)
            
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
            
            self.cover_image.putpixel((x,y), (r, g, b))
            cover_image_pixel_no += 1
        self.cover_image.save("output.png")
        

    def decryptImageFromImage(self, password):

        binDelim = convertToBinary(self.delimeter)
        extractedCT = ""

        for pixel in self.cover_image.getdata():
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
        extractedCT_blocks = ['gAAAA'+e for e in extractedCT.split('gAAAA') if e]
        
        extracted_img = Image.new(mode="RGB", size=(64,64))
        
        crypto = Crypto(password)
        PT_blocks = list(map(crypto.decryptCT, extractedCT_blocks))
        PT_block_bin = list(map(convertToBinary, PT_blocks))
        
        convertBinToNum = lambda a: [int(a[i:i+8], 2) for i in range(0, len(a), 8)]
        PT_block_nums = [convertBinToNum(bin) for bin in PT_block_bin]
        
        convertBlockToPixels = lambda a: [tuple(a[i:i+3]) for i in range(0, len(a), 3)] 
        pixels_blocks = [convertBlockToPixels(block) for block in PT_block_nums]
        
        for block in range(64):
            pixel_idx = 0    
            pixels = pixels_blocks[block]

            column = block % 8 # Block 0->0, 1->1, 2->2, 3->3... 7->7, 8->0, 9->1
            row = block // 8 # Block 0,1,2,3,4,5,6,7->0. 8,9..->1
            
            start = (column * 8, row*8)
            end = ((column+1)*8, (row+1)*8)

            for y in range(start[1], end[1]):
                for x in range(start[0],end[0]):
                    extracted_img.putpixel((x,y), pixels[pixel_idx])
                    pixel_idx += 1
        
        extracted_img.save("extracted.png", 'PNG')

    def saveImage(self):
        dest_filename_without_suffix, _ = os.path.splitext(self.dest_filename)
        dest_img_path = self.head + dest_filename_without_suffix + ".png"
        self.cover_image.save(dest_img_path, "PNG")
        self.unloadImages()
        print("Output file name: ", dest_img_path)
        return dest_img_path

'''
Block 1, 2, 3, 4, 5, 6, 7, 8
row 0
0. 0,0  -> 8,8
1. 8,0  -> 16,8
2. 16,0 -> 24,8
3. 24,0 -> 32,8
4  32,0 -> 40,8
5  40,0 -> 48,8
6  48,0 -> 56,8
7  56,0 -> 64,8

row 1
0 0,8  -> 8,16
1 8,8  -> 16, 16
2 16,8 -> 24, 16
....

for block in range(64):
    column = block % 8 # Block 0->0, 1->1, 2->2, 3->3... 7->7, 8->0, 9->1
    row = block / 8 # Block 0,1,2,3,4,5,6,7->0. 8,9..->1
    
    (column, row) = (0,0), (1,0), (2,0), (3,0)... (7,0)
    
    start = (column * 8, row)
    end   = ((column+1)*8, (row+1)*8)
'''
