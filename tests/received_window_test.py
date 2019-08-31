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
        curses.start_color()
        self.received_window = ReceivedWindow(10, 10, 0, 1)

    def tearDown(self):
        curses.endwin()

    def test_init(self):
        height, width = self.received_window.window.getmaxyx()
        self.assertEqual(height, 10)
        self.assertEqual(width, 10)
        self.assertEqual(self.received_window.cursor.y, 0)
        self.assertEqual(self.received_window.cursor.x, 1)
    
    def test_valid_scroll_up(self):
        self.received_window.top_left.y = 5
        self.received_window.scroll(-1)
        self.assertEqual(self.received_window.top_left.y, 4)

    def test_valid_scroll_down(self):
        self.received_window.height = 11
        self.received_window.scroll(1)
        self.assertEqual(self.received_window.top_left.y, 1)

    def test_invalid_scroll_up(self):
        self.received_window.scroll(-1)
        self.assertEqual(self.received_window.top_left.y, 0)

    def test_invalid_scroll_down(self):
        self.received_window.scroll(1)
        self.assertEqual(self.received_window.top_left.y, 0)

    def test_paint_str_no_scroll(self):
        self.received_window._paint_str("hello", 0)
        self.assertEqual(self.received_window.cursor.y, 1)

    def test_paint_str_scroll(self):
        self.received_window._paint_str("my name is mud", 0)
        self.assertEqual(self.received_window.cursor.y, 2)
    
    def test_paint_message(self):
        self.received_window.paint_message("Mitch", "hello", 0)
        self.assertEqual(self.received_window.cursor.y, 2)

    def test_paint_message_wrap(self):
        self.received_window.paint_message("Zumaad Khan", "hello, world!", 0)
        self.assertEqual(self.received_window.cursor.y, 4)

    # fill two lines then scroll two lines
    def test_paint_message_scroll(self):
        self.received_window.height = 2
        self.received_window.paint_message("Mitch Gamburg", "That's crazy!", 0)
        self.assertEqual(self.received_window.height, 4)
        
    
if __name__ == '__main__':
    unittest.main()