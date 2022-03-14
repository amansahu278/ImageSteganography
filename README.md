# ImageSteganography

While Cryptography deals with hiding the meaning of a message
Steganography deals with hiding the existence of the message itself!

This project implements Image Steganography wherein a cover Image is used where the message is embedded.
The project takes it a step further by encrypting the plain message first and then uses Steganography on the cipher text.

## Usage
  * main.py [-h] -i IMAGE [-p PLAINTEXT] [-e ENCRYPT] [-d DECRYPT]

  * options:
  * -h, --help            show this help message and exit
  * -i IMAGE, --Image IMAGE
                        Cover Image path
  * -p PLAINTEXT, --PlainText PLAINTEXT
                        Plain text to encode
  * -e ENCRYPT, --encrypt ENCRYPT
                        Password/Key for encryption
  * -d DECRYPT, --decrypt DECRYPT
                        Password/Key for decryption

## Implementation details
. The encryption/decryption of text is implemented using the Fernet class of the cryptography package.
. Fernet guarantees that a message encrypted using it cannot be manipulated or read without the key. Fernet is an implementation of symmetric (also known as “secret key”) authenticated cryptography
. All the image manipulation operations are done using the Pillow library


## List of resources
. https://cryptography.io/en/latest/fernet/
. https://auth0.com/blog/image-processing-in-python-with-pillow/
. https://pillow.readthedocs.io/en/stable/reference/Image.html
. https://towardsdatascience.com/hiding-data-in-an-image-image-steganography-using-python-e491b68b1372
