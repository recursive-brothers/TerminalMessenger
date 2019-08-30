import unittest
import sys
import os
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR)
from client_modules.utils import StringBuilder

class StringBuilderTest(unittest.TestCase):
    def setUp(self):
        self.string_builder = StringBuilder("hello hi")

    def tearDown(self):
        pass
    
    def test_append(self):
        self.string_builder._append("yeet")
        self.assertEqual(self.string_builder.build(), "hello hiyeet")
    
    def test_delete(self):
        self.string_builder.delete(1)
        self.assertEqual(self.string_builder.build(),"hello h")
        
    def test_delete_multiple(self):
        self.string_builder.delete(3)
        self.assertEqual(self.string_builder.build(),"hello")
    
    def test_delete_negative(self):
        self.string_builder.delete(-1)
        self.assertEqual(self.string_builder.build(),"hello hi")
    
    def test_addition(self):
        self.string_builder += " zumaad and mitch"
        self.assertEqual(self.string_builder.build(),"hello hi zumaad and mitch")
    
if __name__ == '__main__':
    unittest.main()