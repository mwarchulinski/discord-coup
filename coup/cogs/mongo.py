from datetime import datetime
from coup.bot import Robot
from coup.cogs.base import BaseCog
import motor.motor_asyncio as motor
from umongo import Document, EmbeddedDocument, Instance, fields
from pymongo.collection import Collection

CARDS = {
    'duchesse': {'key': '1', 'name': 'Duchesse'},
    'assassin': {'key': '2', 'name': 'Assassin'},
    'comptesse': {'key': '3', 'name': 'Comptesse'},
    'capitaine': {'key': '4', 'name': 'Capitaine'},
    'ambassadeur': {'key': '5', 'name': 'Ambassadeur'},
    'inquisiteur': {'key': '6', 'name': 'Inquisiteur'}
}


class Card(Document):
    key = fields.StringField(required=True, unique=True)
    name = fields.StringField(required=True)


class Player(EmbeddedDocument):
    id = fields.IntegerField(required=True)
    name = fields.StringField(required=True)
    coins = fields.IntegerField(required=True, default=0)
    cards = fields.ListField(fields.ReferenceField(Card), required=True, default=[])


class Session(Document):
    class State(object):
        WAITING = 'WAITING'
        PLAYING = 'PLAYING'
        COMPLETED = 'COMPLETED'
        DESTROYED = 'DESTROYED'

    guild_id = fields.IntegerField(required=True)
    channel_id = fields.IntegerField(required=True)
    state = fields.StringField(required=True, default=State.WAITING)
    min_players = fields.IntegerField(required=True, default=2)
    max_players = fields.IntegerField(required=True, default=8)
    players = fields.ListField(fields.EmbeddedField(Player, required=True, unique=True), required=True, default=[])
    cards = fields.ListField(fields.ReferenceField(Card), required=True, default=[])
    current = fields.IntegerField(required=True, default=0)
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
            Card,
            Player,
            Session
        ]
        for e in entities:
            setattr(self, e.__name__, self._instance.register(e))

        self.bot.loop.create_task(self.migrate())

    @property
    def db(self) -> Collection:
        return self._db

    async def migrate(self):
        for c in CARDS.values():
            card = await self.Card.find_one({'name': c['name']})
            if not card:
                self.bot.logger.info('Add card {} in database'.format(c))
                card = self.Card(key=c['key'], name=c['name'])
                await card.commit()


def setup(bot: Robot) -> None:
    bot.add_cog(MongoCog(bot))
