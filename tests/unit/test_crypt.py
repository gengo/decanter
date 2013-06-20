import hashlib
import mock
import unittest2 as unittest

from decanter import decanter
from decanter.lib import crypt


class CryptTest(unittest.TestCase):

    def setUp(self):
        self.crypt = crypt.Crypt()
        self.crypt.key = 'test_key'
        self.crypt.padding = 'some_padding'
        self.crypt.block_size = 100

    def test_pad(self):
        s = 'something'
        p = self.crypt.pad(s)
        expected = s + (self.crypt.block_size - len(
            s) % self.crypt.block_size) * self.crypt.padding
        self.assertEqual(p, expected)

    def test_set_padding(self):
        self.crypt.set_padding('padding')
        self.assertEqual(self.crypt.padding, 'padding')

    def test_set_block_size(self):
        self.crypt.set_block_size(255)
        self.assertEqual(self.crypt.block_size, 255)

    def test_get_key_with_self_key(self):
        k = self.crypt.get_key()

        self.assertEqual(k, self.crypt.md5(self.crypt.key))

    def test_get_key_without_self_key(self):
        self.crypt.key = None
        k = self.crypt.get_key('another_key')

        self.assertEqual(k, self.crypt.md5('another_key'))

    def test_get_key_without_keys_raises_exception(self):
        self.crypt.key = None

        with self.assertRaises(Exception) as cm:
            self.crypt.get_key()

        self.assertEqual(
            cm.exception.message, 'Crypt class requires a key to perform encryption/decryption operations')

    def test_md5_returns_hexdigest(self):
        m = hashlib.md5()
        m.update('test')
        h = self.crypt.md5('test')

        self.assertEqual(h, m.hexdigest())

if __name__ == '__main__':
    unittest.main()
