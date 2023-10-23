from dataclasses import dataclass
from decimal import Decimal
import pkgutil
import json
from types import MappingProxyType

from typing import Tuple, List, Iterable, TypeVar, Callable, Mapping


_discord_emoji_dataclass = dataclass(frozen=True)


T = TypeVar("T")


def _identity(x: T) -> T:
    return x


@_discord_emoji_dataclass
class Emoji:
    names: Tuple[str]
    surrogates: str
    unicode_version: Decimal
    category: "EmojiCategory"

    def __iter__(self):
        yield self

    def __str__(self):
        return self.surrogates


@_discord_emoji_dataclass
class DiversityParent(Emoji):
    diversity_children: Tuple["DiversityChild"]

    def __iter__(self):
        yield from super().__iter__()
        for child in self.diversity_children:
            yield from child


@_discord_emoji_dataclass
class DiversityChild(Emoji):
    diversity: Tuple[str]
    diversity_parent: "DiversityParent"


# doesn't actually exist
@_discord_emoji_dataclass
class DiversityInnerNode(DiversityParent, DiversityChild):
    pass


@_discord_emoji_dataclass
class EmojiCategory:
    name: str
    emojis: Tuple[Emoji]

    def __iter__(self):
        for emoji in self.emojis:
            yield from emoji


def _build(data, builder, class_: Callable[[dict], T]) -> T:
    return class_(**{key: mk if data_key is None else mk(data[data_key]) for key, (data_key, mk) in builder.items()})


def _load_diversity(data: List[str]) -> Tuple[str]:
    return tuple(chr(int(d, base=16)) for d in data)


def _load_emoji(data: dict) -> Emoji:
    builder = dict(
        names=("names", tuple),
        surrogates=("surrogates", _identity),
        unicode_version=("unicodeVersion", _identity),
        category=(None, None)
    )
    emoji_class: type(Emoji) = Emoji

    if data.get("hasDiversity", False):
        builder.update(diversity_children=("diversityChildren", _load_emojis))
        emoji_class = DiversityParent

    if data.get("hasDiversityParent", False):
        builder.update(
            diversity=("diversity", _load_diversity),
            diversity_parent=(None, None)
        )
        emoji_class = DiversityChild

    if data.get("hasDiversity", False) and data.get("hasDiversityParent", False):
        emoji_class = DiversityInnerNode

    result: Emoji = _build(data, builder, emoji_class)

    if isinstance(result, DiversityParent):
        for child in result.diversity_children:
            object.__setattr__(child, "diversity_parent", result)  # bypass frozen

    return result


def _load_emojis(data: Iterable[dict]) -> Tuple[Emoji]:
    return tuple(map(_load_emoji, data))


def _load_category(data: dict) -> EmojiCategory:
    builder = dict(
        name=(0, _identity),
        emojis=(1, _load_emojis)
    )

    result = _build(data, builder, EmojiCategory)

    for emoji in result:
        object.__setattr__(emoji, "category", result)  # bypass frozen

    return result


def _load_categories(data: dict) -> Tuple[EmojiCategory]:
    return tuple(map(_load_category, data.items()))


CATEGORIES = _load_categories(
    json.loads(
        pkgutil.get_data(__name__, "data/discord_emoji.json").decode("utf-8")
    )
)


def iter_emojis(categories=CATEGORIES):
    for category in categories:
        yield from category


EMOJIS_BY_NAME: Mapping[str, Emoji] = MappingProxyType(
    {name: emoji for emoji in iter_emojis() for name in emoji.names}
)


EMOJIS_BY_SURROGATES: Mapping[str, Emoji] = MappingProxyType(
    {emoji.surrogates: emoji for emoji in iter_emojis()}
)


def get_unicode_emoji(name):
    return EMOJIS_BY_NAME[name].surrogates