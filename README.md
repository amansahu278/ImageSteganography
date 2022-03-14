# ImageSteganography

While Cryptography deals with hiding the meaning of a message
Steganography deals with hiding the existence of the message itself!

This project implements Image Steganography wherein a cover Image is used where the message is embedded.
The project takes it a step further by encrypting the plain message first and then uses Steganography on the cipher text.

## Usage
usage: main.py [-h] -i IMAGE [-p PLAINTEXT] [-e ENCRYPT] [-d DECRYPT]

options:
  -h, --help            show this help message and exit
  -i IMAGE, --Image IMAGE
                        Cover Image path
  -p PLAINTEXT, --PlainText PLAINTEXT
                        Plain text to encode
  -e ENCRYPT, --encrypt ENCRYPT
                        Password/Key for encryption
  -d DECRYPT, --decrypt DECRYPT
                        Password/Key for decryption
