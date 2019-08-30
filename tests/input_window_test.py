import unittest
import curses
import sys
import os
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR)
from client_modules.input_window import InputWindow



# create our own 'testing framework' for curses later

class InputWindowTest(unittest.TestCase):
  def setUp(self):
    curses.initscr()
    self.input_window = InputWindow(10, 10, 0, 0, 1, 1)

  def tearDown(self):
    curses.endwin()

  def test_init(self):
    height, width = self.input_window.window.getmaxyx()
    self.assertEqual(height, 10)
    self.assertEqual(width, 10)
    self.assertEqual(self.input_window.cursor.y, 1)
    self.assertEqual(self.input_window.cursor.x, 1)

  def test_clear_text(self):
    self.input_window.cursor.y = 2
    self.input_window.cursor.x = 3
    self.input_window.clear_text()

    self.assertEqual(self.input_window.cursor.y, 1)
    self.assertEqual(self.input_window.cursor.x, 1)

  def test_add_str(self):
    self.input_window.add_str('h')
    self.assertEqual(self.input_window.cursor.x, 2)
    self.assertEqual(self.input_window.cursor.y, 1)

  def test_add_str_wrap(self):
    self.input_window.add_str("porkchop")
    self.assertEqual(self.input_window.cursor.x, 1)
    self.assertEqual(self.input_window.cursor.y, 2)
    self.input_window.add_str("all the time")
    self.assertEqual(self.input_window.cursor.x, 5)
    self.assertEqual(self.input_window.cursor.y, 3)
  
  def test_backspace_empty(self):
    self.input_window.backspace()
    self.assertEqual(self.input_window.cursor.x, 1)
    self.assertEqual(self.input_window.cursor.y, 1)

  def test_backspace(self):
    self.input_window.add_str("yeet")
    self.input_window.backspace()
    self.assertEqual(self.input_window.cursor.x, 4)
  
  def test_backspace_wrap(self):
    self.input_window.add_str("hello bob")
    self.assertEqual(self.input_window.cursor.y, 2)
    self.input_window.backspace()
    self.input_window.backspace()
    self.assertEqual(self.input_window.cursor.x, 8)
    self.assertEqual(self.input_window.cursor.y, 1)

   
  #this is hard to test without a specific curses testing library, which we might make ourselves, later.
  # def test_get_input(self):
  #   pass

  
if __name__ == '__main__':
    unittest.main()