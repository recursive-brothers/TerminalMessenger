from abc import ABC, abstractmethod

class ClientInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_chatroom_msgs(self, chatroom_id, limit = 50):
        pass
    
    @abstractmethod
    def insert_msg(self, msg, chatroom_id):
        pass