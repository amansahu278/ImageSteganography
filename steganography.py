# LSB BASED IMAGE STEGANOGRAPHY
import os
from io import BytesIO
import base64
import PIL
import numpy as np
from PIL import Image
from crypto import Crypto

import helpers

NUM_BITS = 10
BLOCK_SIZE = 8*8
_IMAGE_SHAPE = 512
IMAGE_SHAPE = _IMAGE_SHAPE * _IMAGE_SHAPE

def convertToBinary(message):
    """
    Converts input to 8 bit binary equivalent
    """
    if type(message) == str:
        return ''.join([format(ord(i), f'0{NUM_BITS}b') for i in message])
    elif type(message) == bytes:
        return ''.join([format(i, f'0{NUM_BITS}b') for i in message])
    elif type(message) == int or type(message) == np.uint8 or type(message) == np.int64:
        return format(message, f'0{NUM_BITS}b')
    elif type(message) == tuple:
        return [format(i, f'0{NUM_BITS}b') for i in message]
    else:
        raise TypeError("Wrong input type")

def convertBinToString(message):
    message = [message[i : i+NUM_BITS] for i in range(0, len(message), NUM_BITS)]
    return ''.join([chr(int(i, 2)) for i in message])

class ImageSteg:

    def __init__(self, cover_image_path, message_image_path = None):
        ## TODO: Add input for another file, possibly mode functionality too
        self.delimeter = "c3p0"
        self.blocksize = BLOCK_SIZE
        self.message_image_size_crop = (0, 0, _IMAGE_SHAPE, _IMAGE_SHAPE)

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
            if self.message_image_path is not None:
                self.message_image = Image.open(self.message_image_path).convert('RGB')
        except (IOError, FileNotFoundError, PIL.UnidentifiedImageError, ValueError, TypeError) as e:
            print(e)
            exit(1)

    def cropMessageImage(self):
        if self.message_image is not None:
            self.message_image = self.message_image.crop(self.message_image_size_crop)
            self.message_image.save("cropped_msg.png", 'PNG')

    def unloadImages(self):
        self.cover_image.close()
        self.message_image.close()

    def DCT(self, image_chunk):
        image_arr = np.array(image_chunk, dtype=np.int16).reshape((8,8))
        # print("DCT")
        # print("INput image: ", image_arr)
        # image_arr = image_arr - 128
        image_arr = np.subtract(image_arr, 128)
        # print(image_arr)
        get_dct_vec = np.vectorize(helpers.get_dct)
        T = np.fromfunction(lambda i,j: get_dct_vec(i, j, 8), (8,8), dtype='float')
        # print("T: ", T)
        D = np.matmul(T, image_arr)
        # print("T*Image: ", D)
        D = np.matmul(D, T.T)
        # print("DCT: ", D)
        return D

    def Reconstruct(self, image_arr, quant_matrix):
        """
            IDCT
        """
        image_arr = np.array(image_arr).reshape((8,8))
        # print("IDCT: ")
        # print("Image: ", image_arr)
        R = np.multiply(image_arr, quant_matrix)
        # print("Dequantised: ", R)
        get_dct_vec = np.vectorize(helpers.get_dct)
        T = np.fromfunction(lambda i,j: get_dct_vec(i, j, 8), (8,8), dtype='float')        
        # print("T: ", T)
        N = np.matmul(T.T, R)
        N = np.matmul(N, T).astype(int)
        # print("Reconstructed: ", N)
        N = N + 128
        # print("Final: ", N)
        return N
    
    def Quantise(self, input, quant_matrix):
        return np.array(np.around(input/quant_matrix), dtype='int')

    def CodeImage(self, image):
        """
        Converting image block to flat zigzag array
        """
        image = np.array(image).reshape((8,8))
        
        ordering = [[] for i in range(8+8-1)]
        for i in range(8):
            for j in range(8):
                s = i+j
                if s%2 == 0:
                    ordering[s].insert(0, image[i][j])
                else:
                    ordering[s].append(image[i][j])
        
        zigzag = []
        for i in range(len(ordering)):
            for j in range(len(ordering[i])):
                zigzag.append(ordering[i][j])
        
        return np.array(zigzag).flatten()

    def DecodeImage(self, image_arr):
        """
        Recovering 8x8 image block from zigzagged flat array
        """
        image_arr = np.array(image_arr).flatten()

        def jpeg_zigzag_order(n):
            """ Zig-zag reordering of [n x n] matrix
            Keyword arguments:
            n : size of the matrix to be rearranged in zig-zag order
            """

            def move(i, j):
                if j < (n - 1):
                    return max(0, i - 1), j + 1
                else:
                    return i + 1, j

            a = [[0] * n for _ in range(n)]
            x, y = 0, 0
            for v in range(n * n):
                a[y][x] = v
                if (x + y) & 1:
                    x, y = move(x, y)
                else:
                    y, x = move(y, x)
            return a

        zigzag = np.array(jpeg_zigzag_order(8))
        output = np.zeros((8, 8), dtype='int')

        for k in range(len(image_arr)):
            for i in range(8):
                for j in range(8):
                    if zigzag[i, j] == k:
                        output[i, j] = image_arr[k]
        
        return output

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
        print("Extracted!")
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
            chunk_flat = np.array(chunk).flatten()
            chunk_flat_bin = [convertToBinary(i) for i in chunk_flat]
            print(chunk_flat_bin)
            chunk_fin = ''.join(chunk_flat_bin)
            PT_bytes = chunk_fin
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
        print("Embedded!: Check output.png")
        
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
        # extractedCT = extractedCT[:-len(binDelim)]
        # extractedCT = convertBinToString(extractedCT)
       
        
        extractedCT_blocks = ['gAAAA'+e for e in extractedCT.split('gAAAA') if e]
        
        extracted_img = Image.new(mode="RGB", size=(64,64))
        
        crypto = Crypto(password)
        PT_blocks = list(map(crypto.decryptCT, extractedCT_blocks))
        for block in PT_blocks:
            print(len(block))
        # PT_block_bin = list(map(convertToBinary, PT_blocks))
        
        convertBinToNum = lambda a: [int(a[i:i+NUM_BITS], 2) for i in range(0, len(a), NUM_BITS)]
        PT_block_nums = [convertBinToNum(bin) for bin in PT_blocks]
        
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
        print("Extracted!: Check extracted.png")

    def embedImageUsingDCT(self, password):
        cover_image_pixel_no = 0
        w, h = self.cover_image.size
        crypto = Crypto(password)
        CT_chained = bytes()

        for block in range(IMAGE_SHAPE//BLOCK_SIZE):
            # TODO: Change the column, row logic
            column = block % (_IMAGE_SHAPE//8) # Block 0->0, 1->1, 2->2, 3->3... 7->7, 8->0, 9->1
            row = block // (_IMAGE_SHAPE//8) # Block 0,1,2,3,4,5,6,7->0. 8,9..->1
            
            start = (column * 8, row*8)
            end   = ((column+1)*8, (row+1)*8)
            
            chunk = np.array(self.message_image.crop((start[0], start[1], end[0], end[1])))
            # DCT works only on 8x8, meaning we will be making DCT of each band then use them.
            chunk_r, chunk_g, chunk_b = chunk[:, :, 0], chunk[:, :, 1], chunk[:, :, 2]

            # DCT -> Quantize -> CodeImage
            r_code = self.CodeImage(self.Quantise(self.DCT(chunk_r), helpers.QUANTIZATION_MATRIX_90))
            g_code = self.CodeImage(self.Quantise(self.DCT(chunk_g), helpers.QUANTIZATION_MATRIX_90))
            b_code = self.CodeImage(self.Quantise(self.DCT(chunk_b), helpers.QUANTIZATION_MATRIX_90))
            chunk_flat = np.append(r_code, g_code)
            chunk_flat = np.append(chunk_flat, b_code)
            chunk_flat_bin = [convertToBinary(i) for i in chunk_flat]
            PT_byte_string = ''.join(chunk_flat_bin)
            # print("PT Bytes: ", len(PT_byte_string))
            CT = crypto.encryptPT(PT_byte_string)
            # print("CT Len: ", len(CT))
            CT_chained += CT
        
        CT_chained += bytes(self.delimeter, 'utf-8')
        # print("LEN CT_chained: ", len(CT_chained))
        CTbin = convertToBinary(CT_chained)
        # print("LEN CT BIN: ", len(CTbin))
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
        print("Embedded!: Check output.png")

    def decryptImageUsingDCT(self, password):
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

        extractedCT = extractedCT[:-len(binDelim)]
        extractedCT = convertBinToString(extractedCT)
        extractedCT_blocks = ['gAAAA'+e for e in extractedCT.split('gAAAA') if e]
        
        extracted_img = Image.new(mode="RGB", size=(_IMAGE_SHAPE,_IMAGE_SHAPE))
        
        crypto = Crypto(password)
        PT_blocks = list(map(crypto.decryptCT, extractedCT_blocks))
        #PT_Blocks has each block of class str
        
        convertBinToNum = lambda a: [int(a[i:i+NUM_BITS], 2) for i in range(0, len(a), NUM_BITS)]
        PT_block_nums = [convertBinToNum(bin) for bin in PT_blocks]
        # Each num block in PT_block_nums has 192 = 64*3 elements
        
        batchNums = lambda a: [a[i:i+64] for i in range(0, len(a), 64)] 
        blocks_of_nums = [batchNums(block) for block in PT_block_nums]
        for block in blocks_of_nums:
            print(block, len(block))
        # Blocks of nums has blocks of IMAGE_SHAPE/BLOCK_SIZE numbers. 3 such consecutive blocks of numbers form an image block.
        # If image is 64x64, then 64 blocks,
        
        for block in range(IMAGE_SHAPE//BLOCK_SIZE):
            pixel_idx = 0    

            # For each block of numbers, we need to get the org back
            # Decode Image -> Reconstruct image(IDCT)
            r, g, b = blocks_of_nums[block]
            
            r_decoded = self.Reconstruct(self.DecodeImage(r), helpers.QUANTIZATION_MATRIX_90) 
            g_decoded = self.Reconstruct(self.DecodeImage(g), helpers.QUANTIZATION_MATRIX_90) 
            b_decoded = self.Reconstruct(self.DecodeImage(b), helpers.QUANTIZATION_MATRIX_90) 
            
            r = r_decoded.flatten()
            g = g_decoded.flatten()
            b = b_decoded.flatten()

            column = block % (_IMAGE_SHAPE//8) # Block 0->0, 1->1, 2->2, 3->3... 7->7, 8->0, 9->1
            row = block // (_IMAGE_SHAPE//8) # Block 0,1,2,3,4,5,6,7->0. 8,9..->1
            
            start = (column * 8, row*8)
            end = ((column+1)*8, (row+1)*8)

            for y in range(start[1], end[1]):
                for x in range(start[0],end[0]):
                    extracted_img.putpixel((x,y), (r[pixel_idx], g[pixel_idx], b[pixel_idx]))
                    pixel_idx += 1
        
        extracted_img.save("extracted.png", 'PNG')
        print("Extracted!: Check extracted.png")


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
