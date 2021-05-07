import asyncio
import logging
import re
from typing import Any, Dict, Mapping, Optional

import discord
from discord.ext import commands

from .http import GitHubAPI

class RepoData(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> dict:
        cache = ctx.cog.active_prefix_matchers.get(ctx.guild.id, None)
        if cache is None:
            raise commands.BadArgument("There are no configured repositories on this server.")
        repo_data = cache["data"].get(argument, None)
        if repo_data is None:
            raise commands.BadArgument(
                f"There's no repo with prefix `{argument}` configured on this server"
            )
        return repo_data

class RepoNotFound(Exception):
    pass


class ApiError(Exception):
    pass


class Unauthorized(ApiError):
    pass

class GitHubCards(commands.Cog):
    """Get issues for a repo on your Discord Server"""

    def __init__(self, bot):
        self.bot = bot
        self.active_prefix_matchers = {}
        self.splitter = re.compile(r"[!?().,;:+|&/`\s]")
        self._ready = asyncio.Event()
        self.http: GitHubAPI = None  # assigned later on
    
    async def initialize(self):
        """ cache preloading """
        await self.rebuild_cache_for_guild()
        await self._create_client()
        self._ready.set()

    async def rebuild_cache_for_guild(self, *guild_ids):
        self._ready.clear()
        try:
            repos = await self.config.custom("REPO").all()
            data = {int(k): v for k, v in repos.items()}
            if guild_ids:
                data = {k: v for k, v in data.items() if k in guild_ids}

            for guild_id, guild_data in data.items():
                partial = "|".join(re.escape(prefix) for prefix in guild_data.keys())
                pattern = re.compile(rf"^({partial})#([0-9]+)$", re.IGNORECASE)
                self.active_prefix_matchers[int(guild_id)] = {"pattern": pattern, "data": guild_data}
        finally:
            self._ready.set()

    async def cog_before_invoke(self, ctx):
        await self._ready.wait()

    def cog_unload(self):
        self.bot.loop.create_task(self.http.session.close())

    async def _get_token(self, api_tokens: Optional[Mapping[str, str]] = None) -> str:
        """Get GitHub token."""
        if api_tokens is None:
            api_tokens = await self.bot.get_shared_api_tokens("github")

        token = api_tokens.get("token", "")
        if not token:
            log.error("No valid token found")
        return token

    async def _create_client(self) -> None:
        """Create GitHub API client."""
        self.http = GitHubAPI(token=await self._get_token())