import asyncio
import logging
from datetime import timedelta
import secrets
from functools import wraps, partial

from ics.grammar.parse import ContentLine

from aiohttp import web
import ics
import discord
from discord.ext import commands, tasks
import peewee
from cachetools import TTLCache, keys
from asyncache import cached

from owobot.owobot import OwOBot
from owobot.misc import common
from owobot.misc.database import db, Calendar

from typing import AsyncContextManager, Iterable


log = logging.getLogger(__name__)

_CALENDAR_TOKEN_BYTES = 24


def wrap_async_with(cm: AsyncContextManager):
    def impl(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            async with cm:
                return await f(*args, **kwargs)
        return wrapper
    return impl


def _build_ical_event(event: discord.ScheduledEvent, users: Iterable[discord.User] = ()):
    end_time = event.end_time
    if event.entity_type in (discord.EntityType.stage_instance, discord.EntityType.voice):  # no scheduled end time
        end_time = event.start_time + timedelta(hours=1)

    def common_name(user):
        member = event.guild.get_member(user.id)
        return (member if member is not None else user).display_name

    attendees = (
        ics.Attendee(
            email=f"{user.name}#{user.discriminator}",
            **common.nullable_dict(common_name=common_name(user)),
        )
        for user in users
    )

    status = {
        discord.EventStatus.scheduled: "CONFIRMED",
        discord.EventStatus.active: "CONFIRMED",
        discord.EventStatus.completed: "CONFIRMED",
        discord.EventStatus.cancelled: "CANCELLED",
    }.get(event.status, None)

    return ics.Event(
        name=event.name,
        begin=event.start_time,
        end=end_time,
        uid=f"{event.id}@owobot-discord-event",
        **common.nullable_dict(
            description=discord.utils.remove_markdown(event.description) if event.description is not None else None,
        ),
        location=event.location,
        url=f"https://discord.com/events/{event.guild_id}/{event.id}",
        attendees=attendees,
        status=status
    )


def _new_calendar_token():
    return secrets.token_urlsafe(_CALENDAR_TOKEN_BYTES)


def _rid_calendar_token(guild: discord.Guild, user: discord.User):
    Calendar.delete().where(Calendar.guild == guild.id and Calendar.user == user.id).execute()


@db.atomic()
def _give_calendar_token(guild: discord.Guild, user: discord.User) -> str:
    try:
        return Calendar.get(Calendar.guild == guild.id & Calendar.user == user.id).token
    except peewee.DoesNotExist:
        calendar_token = _new_calendar_token()
        Calendar.insert(guild=guild.id, user=user.id, token=calendar_token).execute()
        return calendar_token


class ICal(commands.Cog):
    def __init__(self, bot: OwOBot, http_app: web.Application):
        super().__init__()
        self.bot = bot

        self._app = http_app
        self._add_routes()

    def _add_routes(self):
        base_path = "/api/v0/calendar/{token:[A-Za-z0-9-_=]+}"
        self._app.add_routes((
            web.get(
                base_path + "/user.ics",
                partial(self._handle_calendar, user_only=True),
                name="calendar-user"
            ),
            web.get(
                base_path + "/server.ics",
                partial(self._handle_calendar, user_only=False),
                name="calendar-guild"
            ),
        ))

    async def _handle_calendar(self, request: web.Request, user_only: bool):
        calendar_token = request.match_info["token"]
        try:
            calendar = Calendar.select().where(Calendar.token == calendar_token).get()
        except peewee.DoesNotExist as dne:
            raise web.HTTPNotFound(
                text=f"404: Not Found. No calendar exists with the token {calendar_token}."
            ) from dne

        guild = self.bot.get_guild(calendar.guild)
        user = self.bot.get_user(calendar.user)

        if guild.get_member(user.id) is None:
            raise web.HTTPForbidden(text=f"403: Forbidden. You are no longer a member of that server.")

        return web.Response(
            text=(await self._get_calendar(guild, user if user_only else None)).serialize(),
            content_type="text/calendar"
        )

    @commands.hybrid_group()
    async def calendar(self, ctx: commands.Context):
        pass

    _cache_lock = asyncio.Lock()
    _cache = TTLCache(maxsize=128, ttl=timedelta(days=1).total_seconds())

    def _cache_key(self, guild: discord.Guild, user: discord.User = None):
        del self  # ignore self parameter
        return keys.hashkey(guild, user)

    @cached(_cache, lock=_cache_lock, key=_cache_key)
    async def _get_calendar(self, guild: discord.Guild, user: discord.User = None):
        log.debug(f"cache miss for guild={guild} user={user}")

        cal = ics.Calendar()
        cal.extra.extend((
            ContentLine(name="X-WR-CALNAME", value=guild.name),
            ContentLine(name="X-WR-CALDESC", value=f"Calendar of scheduled events from {guild.name}.")
        ))

        for event in await guild.fetch_scheduled_events():
            event_users = [user async for user in event.users()]
            if user is None or any(event_user == user for event_user in event_users):
                cal.events.add(_build_ical_event(event, users=event_users))

        return cal

    @tasks.loop(minutes=10)
    @wrap_async_with(_cache_lock)
    async def _expire_cache(self):
        """clean up expired cache entries periodically"""
        self._cache.expire()

    @wrap_async_with(_cache_lock)
    async def _again(self, guild: discord.Guild, user: discord.User):
        """remove a user's calendar for a guild from the cache"""
        for c_user in (user, None):
            self._cache.pop(self._cache_key(guild, c_user), None)

    def _give_urls(self, calendar_token):
        joiner = self.bot.config.http_url.join if self.bot.config.http_url is not None else (lambda u: u)
        return tuple(
            joiner(self._app.router[route].url_for(token=calendar_token))
            for route in ("calendar-user", "calendar-guild")
        )

    @calendar.command(brief="get your personal calendar URL for this server")
    async def give(self, ctx: commands.Context, rid=False):
        if rid:
            _rid_calendar_token(ctx.guild, ctx.author)
        calendar_token = _give_calendar_token(ctx.guild, ctx.author)

        user_url, guild_url = self._give_urls(calendar_token)
        await ctx.author.send(
            f"Calendar links for {discord.utils.escape_markdown(ctx.guild.name)}:\n"
            f"‣ only events you are interested in: {user_url}\n"
            f"‣ all events from the server: {guild_url}\n\n"
            "*Use `/calendar rid` to revoke the calendar URLs.*"
        )

        await common.react_success(ctx)

    @commands.cooldown(1, per=timedelta(minutes=5).total_seconds(), type=commands.BucketType.member)
    @calendar.command(brief="remove your calendar for this server from the cache")
    async def again(self, ctx: commands.Context):
        await self._again(ctx.guild, ctx.author)
        await common.react_success(ctx)

    @calendar.command(brief="permanently invalidate your current calendar URL for this server")
    async def rid(self, ctx: commands.Context):
        _rid_calendar_token(ctx.guild, ctx.author)
        await common.react_success(ctx)


def setup(bot: OwOBot):
    return bot.add_cog(ICal(bot, http_app=bot.http_app))
