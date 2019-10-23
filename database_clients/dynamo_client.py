import os
import sys

BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)

import boto3
from boto3.dynamodb.conditions import Key
from uuid import uuid1
from client_interface import ClientInterface
from client_modules.utils import Message

class DynamoClient(ClientInterface):
    def __init__(self):
        self.db = None
        self.messages_table = None
    def connect(self):
        self.db = boto3.resource('dynamodb')
        self.messages_table = self.db.Table("messages")

    def get_chatroom_msgs(self, chatroom_id, limit = 50):
        response = self.messages_table.query(
            # IndexName='timestamp_index',
            ProjectionExpression="messaged_at, message_id, contents, display_name",
            Limit=limit,
            KeyConditionExpression=Key('chatroom_id').eq(chatroom_id)
        )
        return response
    
    def insert_msg(self, msg: Message, chatroom_id):
        self.messages_table.put_item(
            Item={
                'chatroom_id': chatroom_id,
                'messaged_at': msg.fmt_time,
                'message_id': str(uuid1()),
                'contents': msg.msg,
                'display_name': msg.user,
                'username': msg.user
            }
        )