#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random


class Crypt(object):

    """
    Class for simple encryption and decryption using AES cipher in ECB
    Mode
    """

    def __init__(self, key=None):
        self.key = key
        self.padding = "\0"
        self.block_size = 16

    def encrypt(self, data, key=None):
        """ Encrypt the passed data
        data -- the data to encrypt
        key -- (optional if passed from the construct)

        returns the base64 encrypted data
        """
        key = self.get_key(key)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_ECB, iv)
        return base64.b64encode(iv + cipher.encrypt(self.pad((data))))

    def decrypt(self, data, key=None):
        """ Decrypt the passed data
        data -- the data to decrypt, assumed to be a base64 encrypted string
        key -- (optional if passed from the construct)

        returns the decrypted data
        """
        key = self.get_key(key)
        data = base64.b64decode(data)
        iv = data[0:AES.block_size]
        data = data[AES.block_size:]
        cipher = AES.new(key, AES.MODE_ECB, iv)
        return cipher.decrypt(data).strip(self.padding)

    def pad(self, s):
        return s + (self.block_size - len(s) % self.block_size) * self.padding

    def set_padding(self, padding):
        self.padding = padding

    def set_block_size(self, block_size):
        self.block_size = block_size

    def get_key(self, key=None):
        current_key = key if key else self.key
        if not current_key:
            raise Exception(
                'Crypt class requires a key to perform encryption/decryption operations')
        return self.md5(current_key)

    def md5(self, data):
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()
