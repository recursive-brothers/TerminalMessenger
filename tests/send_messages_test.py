import unittest
import sys
import os
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR)
from client_modules.utils import StringBuilder
from client_modules.send_messages import handle_enter, handle_backspace, handle_scroll, handle_normal_ch
from unittest import mock
from client_modules.utils import SCROLL_UP, SCROLL_DOWN


class MockServerSocket(StringBuilder):
    def sendall(self, msg):
        self._append(msg.decode())

class UserHandlingTest(unittest.TestCase):
    def setUp(self):
        self.server_socket = MockServerSocket()

    @mock.patch('client_modules.input_window.InputWindow')
    def test_handle_enter(self, input_window_mock):
        acc_input = StringBuilder("yeet")
        handle_enter(self.server_socket, acc_input, input_window_mock)
        input_window_mock.clear_text.assert_called()
        self.assertEqual(self.server_socket.build(), "yeet")
    
    @mock.patch('client_modules.input_window.InputWindow')
    def test_handle_enter_no_text(self, input_window_mock):
        acc_input = StringBuilder()
        handle_enter(self.server_socket, acc_input, input_window_mock)
        input_window_mock.clear_text.assert_not_called()
        self.assertEqual(self.server_socket.build(), "")

    @mock.patch('client_modules.input_window.InputWindow')
    def test_handle_backspace(self, input_window_mock):
        acc_input = StringBuilder("hello")
        handle_backspace(acc_input, input_window_mock)
        input_window_mock.backspace.assert_called()
        self.assertEqual(acc_input.build(), "hell")

    @mock.patch('client_modules.input_window.InputWindow')
    @mock.patch('client_modules.received_window.ReceivedWindow')
    def test_handle_scroll_up(self,input_window_mock, received_window_mock):
        input_window_mock.get_input.return_value = SCROLL_UP
        handle_scroll(input_window_mock, received_window_mock)
        received_window_mock.scroll.assert_called_once_with(-1)

    @mock.patch('client_modules.input_window.InputWindow')
    @mock.patch('client_modules.received_window.ReceivedWindow')
    def test_handle_scroll_down(self,input_window_mock, received_window_mock):
        input_window_mock.get_input.return_value = SCROLL_DOWN
        handle_scroll(input_window_mock, received_window_mock)
        received_window_mock.scroll.assert_called_once_with(1)

    @mock.patch('client_modules.input_window.InputWindow')
    def test_handle_normal_ch(self, input_window_mock):
        acc_input = StringBuilder("hello")
        handle_normal_ch(ord("e"), acc_input, input_window_mock)
        input_window_mock.add_str.assert_called_once_with("e")
        self.assertEqual(acc_input.build(), "helloe")
    
    
if __name__ == '__main__':
    unittest.main()