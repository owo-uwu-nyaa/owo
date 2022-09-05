import enum
import random
import threading
from copy import deepcopy
import discord
from discord.ext import commands
from recordclass import RecordClass

SIDE_LEN = 4


class Direction(enum.Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class GameState:
    def __init__(self):
        self.board = [[0] * SIDE_LEN for _ in range(SIDE_LEN)]

    def move(self, direction: Direction):
        self._move(direction, self.board)
        self._try_insert_random_empty_loc()

    @staticmethod
    def _move(direction: Direction, board: [[int]]):
        xrange = range(0, SIDE_LEN)
        if direction == Direction.RIGHT:
            xrange = range(SIDE_LEN - 1, -1, -1)
        yrange = range(0, SIDE_LEN)
        if direction == Direction.DOWN:
            yrange = range(SIDE_LEN - 1, -1, -1)
        moved = False
        for y in yrange:
            for x in xrange:
                target_x = x
                target_y = y
                if direction == Direction.UP:
                    target_y -= 1
                if direction == Direction.DOWN:
                    target_y += 1
                if direction == Direction.LEFT:
                    target_x -= 1
                if direction == Direction.RIGHT:
                    target_x += 1
                if not (target_x in xrange and target_y in yrange):
                    continue
                piece = board[y][x]
                target = board[target_y][target_x]
                if piece == target or target == 0:
                    board[target_y][target_x] = piece + target
                    board[y][x] = 0
                    moved = True
        return moved

    def _try_insert_random_empty_loc(self):
        potential_locations = []
        for y in range(0, SIDE_LEN):
            for x in range(0, SIDE_LEN):
                if self.board[y][x] == 0:
                    potential_locations.append((y, x))
        if len(potential_locations) == 0:
            return
        location = random.choice(potential_locations)
        self.board[location[0]][location[1]] = random.choice((2, 4))

    def _has_died(self) -> bool:
        for direction in Direction:
            board = deepcopy(self.board)
            if self._move(direction, board):
                return True
        return False

    def _score(self):
        return sum(map(sum, self.board))

    def __str__(self):
        return (
            "\n\n".join(
                map(
                    lambda row: " ".join(map(lambda tile: str(tile).ljust(4), row)),
                    self.board,
                )
            )
            + f"\n\nScore: {str(self._score())}\nCan make move: {self._has_died()}"
        )


class GameMessage(RecordClass):
    msg_id: int
    chan_id: int
    msg: discord.Message
    game: GameState


class T_game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.game_by_auth: dict[int, GameMessage] = {}
        self.lock = threading.Lock()
        self.direction_lookup = {
            self.config.left_emo: Direction.LEFT,
            self.config.right_emo: Direction.RIGHT,
            self.config.down_emo: Direction.DOWN,
            self.config.up_emo: Direction.UP,
        }

    @commands.hybrid_command(name="2048", brief="play a round of 2048")
    async def t_game(self, ctx):
        game = GameState()
        sent = await ctx.send(f"```{str(game)}```\n\n** **")
        state = GameMessage(msg_id=sent.id, chan_id=ctx.channel.id, game=game, msg=sent)
        with self.lock:
            self.game_by_auth[ctx.author.id] = state
        for key in self.direction_lookup.keys():
            await sent.add_reaction(key)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.update_game(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.update_game(payload)

    async def update_game(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        with self.lock:
            state = self.game_by_auth.get(payload.user_id)
        emoji = str(payload.emoji)
        direction = self.direction_lookup.get(emoji)
        if direction is None:
            return
        if state is None or state.msg_id != payload.message_id:
            return
        state.game.move(direction)
        await state.msg.edit(content=f"```\n{str(state.game)}```\n\n** **")


def setup(bot):
    return bot.add_cog(T_game(bot))
