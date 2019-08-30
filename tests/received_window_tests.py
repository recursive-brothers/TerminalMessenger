import unittest
import curses
import sys
import os
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR)
from client_modules.received_window import ReceivedWindow


class ReceivedWindowTest(unittest.TestCase):
    def setUp(self):
        curses.initscr()

    def tearDown(self):
        curses.endwin()

    def test_init(self):
        pass
    
    def test_scroll(self):
        pass
    
    def test_paint_str(self):
        pass
    
    def paint_message(self):
        pass
    
if __name__ == '__main__':
    unittest.main()