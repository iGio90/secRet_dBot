import time
from mongoengine import *


class CommandLog(Document):
    user_name = StringField(required=True)
    user_id = StringField(required=True)
    stamp = IntField(default=time.time())
    command = StringField(required=True)
