import time
from mongoengine import *


class PullVote(Document):
    pull_id = IntField(required=True, unique=True)
    pull_number = IntField(required=True, unique=True)
    pull_title = StringField()
    points = FloatField(default=0)
    required_points = FloatField(default=0)
    stamp = IntField(default=time.time())
    user_id = IntField(required=True)
    user_name = StringField(required=True)
    votes = DictField()
