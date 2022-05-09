# DCT with ImageSteganography

While Cryptography deals with hiding the meaning of a message
Steganography deals with hiding the existence of the message itself!

The advantage of steganography over cryptography alone is that the intended secret message does not attract attention to itself as an object of scrutiny. 
Plainly visible encrypted messages, no matter how unbreakable they are, arouse interest and may in themselves be incriminating in countries in which encryption is illegal.

This project implements Image Steganography wherein a cover Image is used where the message is embedded.

More specifically, LSB Image Steganography.

The inputted message image is cropped to a size of (64,64,3), following which it undergoes DCT processes before being embedded.

The project takes it a step further by encrypting the plain message first and then uses Steganography on the cipher text.

## Installation
* cd ImageSteganography && pipenv install

## Usage
 * usage: main.py [-h] -i IMAGE [-m MESSAGEIMAGE] [-p PLAINTEXT] [-e ENCRYPT] [-d DECRYPT] [-t TYPE] [-mo MODE]

options:
  * -h, --help            show this help message and exit
  * -i IMAGE, --Image IMAGE
                        Cover Image path
  * -m MESSAGEIMAGE, --MessageImage MESSAGEIMAGE
                        Message image
  * -p PLAINTEXT, --PlainText PLAINTEXT
                        Plain text to encode
  * -e ENCRYPT, --encrypt ENCRYPT
                        Password/Key for encryption
  * -d DECRYPT, --decrypt DECRYPT
                        Password/Key for decryption
  * -t TYPE, --type TYPE  Text embedding or image embedding: t/i
  * -mo MODE, --MODE MODE
                        Mode of embeddeing, normal/dct

## Usage example:
For Image on image without DCT
 * Embedding: python main.py -i <Cover image path> -m <Message image path> -e <Password for encryption> -t "image" -mo "normal"
 * Extraction: python main.py -i output.png -d <Password> -t "image" -mo "normal"
For Image on image with DCT
 * Embedding: python main.py -i <Cover image path> -m <Message image path> -e <Password for encryption> -t "image" -mo "dct"
 * Extraction: python main.py -i output.png -d <Password> -t "image" -mo "dct"
 
 
## To Note:
The cropped message image will be saved as "cropped_msg.png"
The embedded cover image/stego image will be saved as "output.png"
The extracted message image will be saved as "extracted.png"


## List of resources
* https://cryptography.io/en/latest/fernet/
* https://auth0.com/blog/image-processing-in-python-with-pillow/
* https://pillow.readthedocs.io/en/stable/reference/Image.html
* https://www.edureka.co/blog/steganography-tutorial
