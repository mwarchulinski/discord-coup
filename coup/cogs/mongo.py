from datetime import datetime
from coup.bot import Robot
from coup.cogs.base import BaseCog
import motor.motor_asyncio as motor
from umongo import Document, EmbeddedDocument, Instance, fields
from pymongo.collection import Collection


class Player(EmbeddedDocument):
    id = fields.IntegerField(required=True)
    name = fields.StringField(required=True)


class Session(Document):
    class State(object):
        WAITING = 'WAITING'
        PLAYING = 'PLAYING'
        COMPLETED = 'COMPLETED'
        DESTROYED = 'DESTROYED'

    id = fields.IntegerField(attribute='_id')
    guild_id = fields.IntegerField(required=True)
    channel_id = fields.IntegerField(required=True)
    state = fields.StringField(required=True, default=State.WAITING)
    min_players = fields.IntegerField(required=True, default=2)
    max_players = fields.IntegerField(required=True, default=8)
    players = fields.ListField(fields.EmbeddedField(Player), required=True, default=[])
    message_id = fields.IntegerField(required=False)
    created_at = fields.DateTimeField(required=True, default=datetime.utcnow())
    finished_at = fields.BooleanField(required=False)

    def find_player_by_id(self, id: int) -> Player:
        for p in self.players:
            if p.id == id:
                return p
        return None


class MongoCog(BaseCog):

    def __init__(self, bot: Robot):
        super().__init__(bot)
        self._client = motor.AsyncIOMotorClient(bot.config.get('mongo').get('uri'), io_loop=bot.loop)
        self._db = self._client[bot.config.get('mongo').get('db')]
        self._instance = Instance(self._db)

        entities = [
            Player,
            Session
        ]
        for e in entities:
            setattr(self, e.__name__, self._instance.register(e))

    @property
    def db(self) -> Collection:
        return self._db


def setup(bot: Robot) -> None:
    bot.add_cog(MongoCog(bot))
