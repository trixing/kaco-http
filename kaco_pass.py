# Written by Jan Dittmer <jdi@l4x.org>
# Based heavily on code from
# https://gist.github.com/franzwarning/1e5fab9d7d2e90086e567768e71904be
# and
# The Kaco NX Setup APK
#
# The password checking code (widgets/dialog/InvVerificationDialog.java)
# String generatePasswordL4 = CipherUtil.generatePasswordL4(AES.Encrypt(this.isn).trim());
# generatePasswordL4.equalsIgnoreCase(str.trim()
#

from Cryptodome.Cipher import AES
from Cryptodome import Random

import base64
import hashlib
import random
import sys


def pad(plain_text):
    """
    func to pad cleartext to be multiples of 8-byte blocks.
    If you want to encrypt a text message that is not multiples of 8-byte blocks, 
    the text message must be padded with additional bytes to make the text message to be multiples of 8-byte blocks.
    """
    block_size = AES.block_size
    number_of_bytes_to_pad = block_size - len(plain_text) % block_size
    ascii_string = chr(number_of_bytes_to_pad)
    padding_str = number_of_bytes_to_pad * ascii_string
    padded_plain_text =  plain_text + padding_str
    return padded_plain_text


def generatePassword(isn):
    plain = pad(isn)
    key = 'KA%C!200@121^23_'   # top secret

    # AES.java

    cipher = AES.new(bytes(key.encode('UTF-8')), AES.MODE_ECB)
    encrypted_bytes = cipher.encrypt(bytes(plain.encode('UTF-8')))

    encrypted_text = base64.b64encode(encrypted_bytes).decode("utf-8")
    print('Encrypted Text: ' + encrypted_text)

    # CipherUtil.java
    # encodeByMD5
    # byteArrayToHexString(MessageDigest.getInstance("MD5").digest(str.getBytes())).toUpperCase();
    md5_text = hashlib.md5(encrypted_text.encode('utf-8')).hexdigest().upper()
    print('MD5 Text: ' + md5_text)

    # generatePasswordL16 return encodeByMD5(str).substring(8, 24);
    l16_text = md5_text[8:24]
    print('L16 Text: ' + l16_text)

    # generatePasswordL4 return generatePasswordL16(str).substring(3, 7);
    l4_text = l16_text[3:7]
    print('L4 Text (your key): ' + l4_text)

    return l4_text


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Need to provide ISN, e.g. 8.0NX312001234, as argument')
        sys.exit(1)
    generatePassword(sys.argv[1])
