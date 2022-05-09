# DCT with ImageSteganography

While Cryptography deals with hiding the meaning of a message
Steganography deals with hiding the existence of the message itself!

The advantage of steganography over cryptography alone is that the intended secret message does not attract attention to itself as an object of scrutiny. 
Plainly visible encrypted messages, no matter how unbreakable they are, arouse interest and may in themselves be incriminating in countries in which encryption is illegal.

This project implements Image Steganography wherein a cover Image is used where the message is embedded.

More specifically, LSB Image Steganography.

The inputted message image is cropped to a size of (64,64,3), following which it undergoes DCT processes before being embedded.

The project takes it a step further by encrypting the plain message first and then uses Steganography on the cipher text.

## Installation (try using linux)
* pip install pipenv
* cd ImageSteganography-DCT
* pipenv install
* pipenv shell
* Run the usage commands shown below
* If any errors had occured during pipenv install, or any module is missing, repeat install of those libraries using pip install library-name

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
1. For Image on image without DCT
 * Embedding: python main.py -i "Cover image path" -m "Message image path" -e "Password for encryption" -t "image" -mo "normal"
 * Extraction: python main.py -i "output.png" -d 'Password of your choice' -t "image" -mo "normal"
2. For Image on image with DCT
 * Embedding: python main.py -i "Cover image path" -m "Message image path" -e "Password for encryption" -t "image" -mo "dct"
 * Extraction: python main.py -i "output.png" -d 'Password of your choice' -t "image" -mo "dct"
 
 
## To Note:
The cropped message image will be saved as "cropped_msg.png"
The embedded cover image/stego image will be saved as "output.png"
The extracted message image will be saved as "extracted.png"


## List of resources
* https://cryptography.io/en/latest/fernet/
* https://auth0.com/blog/image-processing-in-python-with-pillow/
* https://pillow.readthedocs.io/en/stable/reference/Image.html
* https://www.edureka.co/blog/steganography-tutorial

* https://www.math.cuhk.edu.hk/~lmlui/dct.pdf
* https://github.com/andreacos/BoostingCNN-Jpeg-Primary-Quantization-Matrix-Estimation/blob/b4bd209595c1dbd27841c47314a3a1b3af576f7d/utils.py#L232
* https://arxiv.org/pdf/1912.10789.pdf
* https://users.cs.cf.ac.uk/Dave.Marshall/Multimedia/node231.html 
