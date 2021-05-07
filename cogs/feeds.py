import re
import aiohttp
import feedparser
from datetime import datetime, timezone

import discord
from discord.ext import tasks, commands

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class GitHub(commands.Cog):
    """
    Feed for GitHub
    """

    def __init__(self, bot):
        self.bot = bot
        self._github_rss.start()

        self.color = 0x7289da
        self.githubURL = r"https://github.com/(.*?)/(.*?)/?"
        self.invalid = "Invalid GitHub URL"

    def cog_unload(self):
        self._github_rss.cancel()

    @staticmethod
    async def commit_embed(entry, gh_link):
        title_regex = r"https://github.com/.*?/(.*?)/commits/(.*)"
        title = re.fullmatch(title_regex, gh_link)
        title = f"[{title.group(1)}:{title.group(2)}] 1 new commit"

        desc_regex = r"https://github.com/.*?/.*?/commit/(.*)"
        desc = re.fullmatch(desc_regex, entry.link).group(1)[:7]
        desc = f"[`{desc}`]({entry.link}) {entry.title} – {entry.author}"
        t = datetime.strptime(entry.updated, TIME_FORMAT).replace(tzinfo=timezone.utc)
        e = discord.Embed(title=title, color=0x7289da, description=desc, url=entry.link, timestamp=t)
        e.set_author(name=entry.author, url=entry.href, icon_url=entry.media_thumbnail[0]["url"])
        return e

    @staticmethod
    async def commit_embeds(entries, gh_link, url):
        title_regex = r"https://github.com/.*?/(.*?)/commits/(.*)"
        title = re.fullmatch(title_regex, gh_link)

        commits_regex = r"(https://github.com/.*?/.*?)/.*"
        commits_link = f"{re.fullmatch(commits_regex, url).group(1)}/commits"

        desc_regex = r"https://github.com/.*?/.*?/commit/(.*)"
        desc = ""
        num = 0
        for e in entries:
            if num >= 10: break
            desc0 = re.fullmatch(desc_regex, e.link).group(1)[:7]
            desc += f"[`{desc0}`]({e.link}) {e.title} – {e.author}\n"
            num += 1
        title = f"[{title.group(1)}:{title.group(2)}] {num} new commits"
        t = datetime.strptime(entries[0].updated, TIME_FORMAT).replace(tzinfo=timezone.utc)
        e = discord.Embed(title=title, color=0x7289da, description=desc, url=commits_link, timestamp=t)

        e.set_author(name=entries[0].author, url=entries[0].href, icon_url=entries[0].media_thumbnail[0]["url"])
        return e

    @staticmethod
    async def new_entries(entries, last_time):
        new_time = datetime.utcnow()
        new_entries = []
        for e in entries:
            e_time = datetime.strptime(e.updated, TIME_FORMAT)
            if e_time > last_time:
                new_entries.insert(0, e)
            else:
                break
        return new_entries, new_time