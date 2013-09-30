import unittest2 as unittest

from decanter.lib.singleton import Singleton


class TestSingleton(Singleton):
    pass


class SingletonTest(unittest.TestCase):

    def test_same_instance(self):
        self.assertTrue(TestSingleton() is TestSingleton())
        self.assertTrue(TestSingleton.get_instance() is TestSingleton.get_instance())
        self.assertTrue(TestSingleton() is TestSingleton.get_instance())

    def test_hold_value(self):
        singletonA = TestSingleton()
        singletonA.value = "This is value."
        self.assertEqual(singletonA.value, TestSingleton().value)


if __name__ == '__main__':
    unittest.main()
