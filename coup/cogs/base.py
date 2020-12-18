import discord.ext.commands as commands
from coup.bot import Robot


class BaseCog(commands.Cog):

    def __init__(self, bot: Robot):
        self._bot = bot

    @property
    def bot(self) -> Robot:
        return self._bot
