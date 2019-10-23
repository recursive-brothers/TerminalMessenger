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
        self.chatroom_id = 'c7532c20-e301-11e9-aaef-0800200c9a66'

    def connect(self):
        self.db = boto3.resource('dynamodb')

    def get_chatroom_msgs(self, chatroom_id, limit = 50):
        pass
        # response = self.messages_table.query(
        #     IndexName='timestamp_index',
        #     ProjectionExpression="#yr, title, info.genres, info.actors[0]",
        #     KeyConditionExpression=Key('year').eq(1992) & Key('title').between('A', 'L')
        # )
    
    def insert_msg(self, msg: Message, chatroom_id):
        self.db.put_item(
            TableName='messages',
            Item={
                'chatroom_id': self.chatroom_id,
                'messaged_at': msg.time,
                'message_id': str(uuid1()),
                'contents': msg.msg,
                'display_name': msg.user,
                'username': msg.user
            }
        )
