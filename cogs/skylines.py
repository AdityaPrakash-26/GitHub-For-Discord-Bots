import aiohttp
import logging
from datetime import datetime as dt

import discord
from discord.ext import commands


class GithubSkylines(commands.Cog):
    """Create a skyline of your contributions on github."""

    def __init__(self, bot):
        self.bot = bot
        self.skyline = "https://skyline.github.com/{}"
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
        log.debug("Session closed.")

    @commands.command()
    async def githubskyline(self, ctx, git_username: str, year: int):
        """Get your github skyline for a particular year."""
        await ctx.trigger_typing()
        async with self.session.get(self.skyline.format(git_username)) as session:
            if not session.status == 200:
                return await ctx.send("Please enter a valid github username.")
        if not year in [*range(2008, int(dt.now().strftime("%Y"))+1)]:
            return await ctx.send(
                f"Please enter a valid year, between 2008 and {dt.now().strftime('%Y')}."
            )
        msg = "Your GitHub Sky Line is:\n"
        msg += self.skyline.format(git_username) + f"/{year}"
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(GithubSkylines)