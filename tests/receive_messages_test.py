import unittest
import sys
import os
from unittest import mock
import datetime
import json
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR)
from client_modules.receive_messages import format_metadata, determine_sender
from client_modules import utils



utils.USERNAME = "Mitch & Zumaad"

class MockServerSocket:
    def recv(self, _arg):
        message = {"message": "hello", "address": 2, "name": "Mitch"}
        return json.dumps(message).encode()

class SocketReceiverTest(unittest.TestCase):
    def setUp(self):
        self.server_socket = MockServerSocket()

    def test_determine_sender_terminal(self):
        sender = determine_sender("Mitch & Zumaad")
        self.assertEqual(sender, utils.SENDER.SELF.value)

    def test_determine_sender_self(self):
        sender = determine_sender("Terminal Messenger")
        self.assertEqual(sender, utils.SENDER.TERMINAL.value)

    def test_determine_sender_other(self):
        sender = determine_sender("This is unrelated")
        self.assertEqual(sender, utils.SENDER.OTHER.value)

    @mock.patch('datetime.datetime')
    def test_format_metadata(self, mock_date):
        time = datetime.datetime.now()
        formatted_time = time.strftime("%Y-%m-%d %H:%M")

        mock_date.now.return_value = time

        formatted_metadata = format_metadata("Zumaad")
        self.assertEqual(formatted_metadata, f"Zumaad     {formatted_time}")

if __name__ == '__main__':
        unittest.main()
