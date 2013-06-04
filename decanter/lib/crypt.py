#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
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
        if key:
            self.key = key
        if not self.key:
            raise Exception("Missing encryption key")

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_ECB, iv)
        return base64.b64encode(iv + cipher.encrypt(self.pad((data))))


    def decrypt(self, data, key=None):
        """ Decrypt the passed data
        data -- the data to decrypt, assumed to be a base64 encrypted string
        key -- (optional if passed from the construct)

        returns the decrypted data
        """
        if key:
            self.key = key
        if not self.key:
            raise Exception("Missing decryption key")

        data = base64.b64decode(data)
        iv = data[0:AES.block_size]
        data = data[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_ECB, iv)
        return cipher.decrypt(data).strip(PADDING)


    def pad(self, s):
        return s + (self.block_size - len(s) % self.block_size) * self.padding


    def set_padding(self, padding):
        self.padding = padding


    def set_block_size(self, block_size):
        self.block_size = block_size
