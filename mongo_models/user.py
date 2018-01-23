from mongoengine import *


class User(Document):
    discord_id = IntField(unique=True)
    discord_name = StringField()
    discord_mention = StringField()
    git_user_id = IntField(required=True, unique=True)
    git_user_name = StringField(required=True)
    points = FloatField(default=0)
