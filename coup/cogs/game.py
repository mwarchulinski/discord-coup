import discord.ext.commands as commands
import pymongo
from coup.bot import Robot
from coup.cogs.base import BaseCog
from coup.cogs.mongo import Session
import coup.embeds as embeds


class GameCog(BaseCog):

    # FIXME move this code to a specialized class
    async def find_current_session(self, ctx: commands.Context) -> Session:
        await self.bot.mongo.Session.find_one({
            'guild_id': ctx.guild.id,
            'channel_id': ctx.channel.id,
            'state': {'$nin': [Session.State.DESTROYED]},
        }, sort=[
            ('created_at', pymongo.DESCENDING)
        ])

    @commands.command(name='create')
    async def cmd_create(self, ctx: commands.Context) -> None:
        """
        requires:
        - session not exists
        """
        session = await self.find_current_session(ctx)
        if session:
            return

        player = self.bot.mongo.Player(
            id=ctx.author.id,
            name=ctx.author.name
        )

        session = self.bot.mongo.Session(
            guild_id=ctx.guild.id,
            channel_id=ctx.channel.id,
            players=[player]
        )
        await session.commit()

        self.bot.logger.info('Game session #{} created'.format(session.id))

        message = await ctx.send(embed=embeds.create_game_info(session))

        session.message_id = message.id
        await session.commit()

    @commands.command(name='destroy')
    async def cmd_destroy(self, ctx: commands.Context) -> None:
        """
        requires:
        - session exists
        """
        session = await self.find_current_session(ctx)
        if not session:
            return

        session.state = Session.State.DESTROYED
        await session.commit()

        self.bot.logger.info('Game session #{} destroyed'.format(session.id))

        if session.message_id:
            message = await ctx.channel.fetch_message(session.message_id)
            await message.edit(embed=embeds.create_game_info(session))

    @commands.command(name='show')
    async def cmd_show(self, ctx: commands.Context) -> None:
        """
        requires:
        - session exists
        """
        session = await self.find_current_session(ctx)
        if not session:
            return

        message = await ctx.send(embed=embeds.create_game_info(session))

        session.message_id = message.id
        await session.commit()

    @commands.command(name='join')
    async def cmd_join(self, ctx: commands.Context) -> None:
        """
        requires:
        - session exists
        - session.state = WAITING
        - len(session.players) < session.max_players
        """
        session = await self.find_current_session(ctx)
        if not session:
            return

        if session.state != Session.State.WAITING:
            return

        player = session.find_player_by_id(ctx.author.id)
        if player:
            return

        if len(session.players) >= session.max_players:
            return

        player = self.bot.mongo.Player(
            id=ctx.author.id,
            name=ctx.author.name
        )
        session.players.append(player)
        await session.commit()

        self.bot.logger.info('{} join game session #{}'.format(player.name, session.id))

        if session.message_id:
            message = await ctx.channel.fetch_message(session.message_id)
            await message.edit(embed=embeds.create_game_info(session))

    @commands.command(name='start')
    async def cmd_start(self, ctx: commands.Context) -> None:
        """
        requires:
        - session exists
        - session.state = WAITING
        - len(session.players) >= session.min_players
        """
        session = await self.find_current_session(ctx)
        if not session:
            return

        if session.state != Session.State.WAITING:
            return

        if len(session.players) < session.min_players:
            return

        session.state = Session.State.PLAYING
        await session.commit()

        if session.message_id:
            message = await ctx.channel.fetch_message(session.message_id)
            await message.edit(embed=embeds.create_game_info(session))


def setup(bot: Robot) -> None:
    bot.add_cog(GameCog(bot))
