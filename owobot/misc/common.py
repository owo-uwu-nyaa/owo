from __future__ import annotations

import contextlib
import datetime
import functools
import re
import io
import itertools as it
from collections import namedtuple
import textwrap

import discord
import emoji
from discord.ext import commands
from peewee import PeeweeException
from owobot.misc.database import Owner
from typing import List, Iterable, Optional, TypeVar, Callable, Any, overload

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


def get_nick_or_name(user: object) -> str:
    gnick = (
        user.nick
        if isinstance(user, discord.Member) and not user.nick is None
        else user.name
    )
    return re.sub(r"[@!$`]", "", gnick)


async def author_id_to_obj(bot, author_id, ctx):
    author = ctx.guild.get_member(author_id)
    if author is None:
        author = await bot.fetch_user(author_id)
    return author


def ellipsize(msg, max_length, overflow="..."):
    # TODO: breaks markdown
    return (
        f"{msg[: max_length - len(overflow)].rstrip()}{overflow}"
        if len(msg) > max_length
        else msg
    )


def ellipsize_sub(pattern: re.Pattern | str,
                  replacement: str | callable,
                  text: str,
                  max_length: int,
                  overflow="...",
                  safe_replacement=None):
    """like ``re.sub``, but limit to ``max_length``, including ``overflow`` if truncated"""
    if max_length < len(overflow):
        return ""
    replace = replacement if callable(replacement) else (lambda m: m.expand(replacement))
    safe_replace = (
        (safe_replacement if callable(safe_replacement) else (lambda m: m.expand(safe_replacement)))
        if safe_replacement is not None
        else lambda m: ""
    )

    parts = []
    prev_result_end = 0
    for match in re.finditer(pattern, text):
        parts.append((text[prev_result_end:match.start()], replace(match), match))
        prev_result_end = match.end()
    parts.append((text[prev_result_end:], "", None))
    total_length = sum(len(p) + len(r) for p, r, _ in parts)

    def make_result(r_parts, r_safe=()):
        return "".join(it.chain(it.chain.from_iterable((p, r) for p, r, _ in r_parts), r_safe))
    if total_length <= max_length:
        return make_result(parts)

    max_length = max_length - len(overflow)
    safes = []
    while total_length > max_length:
        plain, repl, match = parts.pop()
        item_len = len(repl) + len(plain)
        safes.extend((safe_replace(match) if match is not None else "", plain))
        if total_length - item_len <= max_length:
            break
        total_length -= item_len
    return make_result(parts, reversed(safes))[:max_length] + overflow


def paginate(msg, max_page_len):
    # TODO: breaks markdown
    """Result is an iterator of pages. Each page will be at most ``max_page_len`` long."""
    pages = [[]]
    page_len = 0
    for paragraph in msg.split("\n"):
        # add length of last page to account for newlines after adding to page
        if len(pages[-1]) + page_len + len(paragraph) > max_page_len and page_len > 0:
            pages.append([])
            page_len = 0

        if len(paragraph) > max_page_len:
            # here, we are always at the beginning of a page
            assert page_len == 0
            # remove the empty page
            pages.pop()
            w_pages = textwrap.wrap(
                paragraph,
                width=max_page_len,
                placeholder="",
                expand_tabs=False,
                replace_whitespace=False,
                drop_whitespace=False,
            )
            pages.extend([p] for p in w_pages)
            page_len = len(w_pages[-1])
        else:
            pages[-1].append(paragraph)
            page_len += len(paragraph)

    return ("\n".join(page) for page in pages)


async def send_paginated(to: discord.abc.Messageable, *args, page_length=2000, **kwargs):
    if len(args) > 1:
        raise ValueError("unexpected argument")
    pages = list(paginate(args[0], page_length)) if args else (discord.utils.MISSING, )
    first_only = ("thread_name", )
    last_only = ("file", "files", "embed", "embeds", "view", "wait")
    first_message_kwargs = {k: v for k, v in kwargs.items() if k in first_only}
    last_message_kwargs = {k: v for k, v in kwargs.items() if k in last_only}
    per_message_kwargs = {k: v for k, v in kwargs.items() if k not in first_only and k not in last_only}
    messages = []
    last_index = len(pages) - 1
    for i, page in enumerate(pages):
        messages.append(await to.send(
            page,
            **nullable_dict(wait=True if i < last_index and isinstance(to, discord.Webhook) else None),
            **per_message_kwargs,
            **(first_message_kwargs if i == 0 else dict()),
            **(last_message_kwargs if i == last_index else dict())
        ))
    return messages if kwargs.get("wait", False) else None


_media_embed_types = ("image", "video", "gifv")


async def message_as_embedded_reply(message, max_length=256):
    thumbnail = next(
        it.chain(
            (
                em.thumbnail
                for em in message.embeds
                if em.type in _media_embed_types and em.thumbnail
            ),
            (att for att in message.attachments if att.width and att.height),
        ),
        None,
    )

    # hide the original message if it's empty (e.g. upload-only) or just a URL
    elide_message = not message.content or (
        thumbnail is not None and thumbnail.url == message.content
    )

    reply_embed = discord.Embed(
        # embed character limit: 6000
        description=""
        if elide_message
        else sanitize_send(ellipsize(message.content, max_length)),
        # timestamp=reply_to.created_at,  # ugly
        # title="reply to ...",  # together with url, could be used to link to message, also ugly
        # url=reply_to.jump_url,
    )
    if thumbnail is not None:
        reply_embed.set_thumbnail(url=thumbnail.url)
    reply_embed.set_author(
        name=f"↩️ {message.author.display_name}",
        # url=message.author.jump_url,  # message.jump_url is used instead
        url=message.jump_url,
        icon_url=message.author.display_avatar.url,
    )
    return reply_embed


markdown_chars_re = re.compile(r"[~_*`]")


def sanitize_markdown(text: str) -> str:
    # prepend each markdown interpretable char with a zero width space
    # italics with a single * seems to not break codeblocks
    return markdown_chars_re.sub(r"​\0", text)


def sanitize_send(text: str) -> str:
    if not text or emoji.is_emoji(text[0]):
        return text
    return re.sub(r"^[^\w<>()@*_~`]+", "", text)


async def is_owner(ctx: commands.Context):
    if Owner.select().where(Owner.snowflake == ctx.author.id).exists():
        return True
    await react_failure(ctx)
    return False


def remove_prefix(*, prefix: str, content: str) -> Optional[str]:
    if content.startswith(prefix):
        return content[len(prefix):]


async def react(ctx: commands.Context, reaction, details=None):
    if ctx.message.type == discord.MessageType.default:
        await ctx.message.add_reaction(reaction)
    elif ctx.interaction:
        await ctx.send(reaction + (" " + details if details is not None else ""))


async def react_success(ctx: commands.Context, details="success"):
    await react(ctx, "✅", details)


async def react_failure(ctx: commands.Context, details="an error occurred"):
    await react(ctx, "❌", details)


async def react_empty(ctx: commands.Context, details="empty"):
    await react(ctx, "🧺", details)


async def try_exe_cute_query(ctx: commands.Context, query):
    try:
        res = query.execute()
        await react_success(ctx)
        return res
    except PeeweeException as e:
        await react_failure(ctx, str(e))


# from https://github.com/janin-s/ki_pybot/blob/8d1cf55aaafe991bd8e021c8d72e5df5e0ee42de/lib/utils/trading_utils.py#L247
def seconds_until(hours: int, minutes: int) -> float:
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

    return (future_exec - now).total_seconds()


class IdentityConverter(commands.Converter):
    """
    Variadic arguments are not supported in slash commands, and probably never will be
    (because discord, see https://github.com/discord/discord-api-docs/discussions/3286).
    Use :class:`commands.Greedy[IdentityConverter] <commands.Greedy>` to simulate variadic arguments
    that work in both slash and regular commands."""
    async def convert(self, ctx: commands.Context, argument: str):
        return argument


Variadic = Annotated[List[str], commands.Greedy[IdentityConverter]]


def long_running_command(f):
    """Commands annotated with `long_running_command` will show a typing indicator for their entire duration."""
    @functools.wraps(f)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        async with ctx.typing():
            await f(self, ctx, *args, **kwargs)
    return wrapper


def nullable_dict(**kwargs):
    return dict((k, v) for k, v in kwargs.items() if v is not None)


def redirect_string_io_std_streams():
    stdout, stderr = io.StringIO(), io.StringIO()

    @contextlib.contextmanager
    def manager():
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            yield

    return stdout, stderr, manager


T = TypeVar("T")


@overload
def minima(iterable: Iterable[T], key: Callable[[T], Any] = None, reverse=False) -> List[T]:
    ...


@overload
def minima(item1: T, item2: T, *items: T, key: Callable[[T], Any] = None, reverse=False) -> List[T]:
    ...


def minima(*iterable_or_items: T | Iterable[T], key: Callable[[T], Any] = None, reverse=False) -> List[T]:
    if len(iterable_or_items) < 1:
        raise TypeError("expected at least one argument")

    iterable = iterable_or_items if len(iterable_or_items) > 1 else iterable_or_items[0]
    key = key if key is not None else (lambda x: x)

    curr_minima = []
    curr_min_key = None

    for item in iterable:
        item_key = key(item)
        if not curr_minima or (item_key < curr_min_key if not reverse else item_key > curr_min_key):
            curr_minima = [item]
            curr_min_key = item_key
        elif item_key == curr_min_key:
            curr_minima.append(item)

    return curr_minima


_DISCORD_LINK_RE = re.compile(r".*?(?P<scheme>https?)://(?P<netloc>\S{2,})")
linkify_result = namedtuple("linkify_result", ("scheme", "netloc", "start", "end"))


def discord_linkify_likely(s: str) -> Optional[linkify_result]:
    """
    discord link handling is wack

    - scheme may only be http or https
    - any text may precede the ``http(s)://`` (scheme), it will not be part of the link
    - any text may follow after the scheme, it will be part of the link
    - the link continues until whitespace, except a ``)`` at the last position
    - unless there is (at least one) ``(`` somewhere after the scheme (they don't need to be match correctly)
    - the text after the scheme must be at least two characters long, but if the last character is a ``)`` as above,
      the link can end up being only a single character
    - this is all wrong, because then discord processes the link some more??
    - ``https://.x`` -> ``https://.x`` but ``https://.()`` -> ``https://./()``
      and ``https://1$`` -> ``https://1/$`` but ``https://!$`` -> ``None``
    - ``https://x@y`` -> ``https://y``
    - ``https://$/1`` -> ``None``, ``https://^^`` -> ``None``
    """
    match = _DISCORD_LINK_RE.fullmatch(s)
    if match:
        scheme, netloc = match.group("scheme", "netloc")
        start = match.start("scheme")
        end = match.end("netloc")

        # last character is a bracket: check if all preceding opening brackets are closed
        if netloc[-1] == ")":  # len(netloc) >= 2, indexing is safe
            bracket_count = 0
            for c in netloc[:-1]:
                if c == "(":
                    bracket_count += 1
                elif c == ")" and bracket_count > 0:
                    bracket_count -= 1
            if not bracket_count:
                # last bracket is not part of link
                netloc = netloc[:-1]
                end -= 1

        return linkify_result(scheme=scheme, netloc=netloc, start=start, end=end)


def _anext(iterator, *args):
    """for python < 3.10, from
    https://github.com/python/cpython/blob/487135a396a504482ae3a7e9c7f80a44627a5a3f/Lib/test/test_asyncgen.py#L54"""
    if len(args) > 1:
        raise TypeError(f"anext expected at most 2 arguments, got {len(args) + 1}")

    try:
        __anext__ = type(iterator).__anext__
    except AttributeError:
        raise TypeError(f'{iterator!r} is not an async iterator')

    if not args:
        return __anext__(iterator)

    async def anext_impl():
        try:
            return await __anext__(iterator)
        except StopAsyncIteration:
            return args[0]

    return anext_impl()


try:
    anext = anext
except NameError:
    anext = _anext
