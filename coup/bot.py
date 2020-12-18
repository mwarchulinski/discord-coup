import sys
import os
import json
import logging
import discord
import discord.ext.commands as commands


class Robot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix='!', activity=discord.Activity(name='Coup | !help'))
        self._config = None
        self._logger = None
        self._init_logging()
        self._load_config()
        self._load_extensions()

    @property
    def config(self) -> dict:
        return self._config

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def mongo(self) -> 'MongoCog':
        return self.get_cog('MongoCog')

    def _init_logging(self) -> None:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(fmt='%(levelname)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)

        self._logger = logging.getLogger('bot')
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(handler)

    def _load_config(self) -> None:
        self.logger.info('Load configuration')
        filename = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        with open(filename, 'r') as fp:
            self._config = json.load(fp)
        self.command_prefix = self._config.get('command_prefix', '!')

    def _load_extensions(self) -> None:
        extensions = ('mongo', 'game')
        for ext in extensions:
            self.logger.info('Load extension {}'.format(ext))
            self.load_extension('coup.cogs.{}'.format(ext))

    async def on_ready(self) -> None:
        self.logger.info('Bot is ready')
