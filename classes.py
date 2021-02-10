from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gameManager import GameManager

import asyncio
from typing import Optional
from uuid import UUID

from Chessnut import Game as Game
from stockfish import Stockfish


@dataclass
class GameOptions:
    ai_is_white: Optional[bool] = False
    ai_diff: int = 10


@dataclass
class ChessGame:
    game: Game = Game()
    opts: GameOptions = GameOptions()
    stockfish: Stockfish = None
    timer: asyncio.Task = None


async def delete_match_in(gm: "GameManager", uid: UUID, seconds=3600):
    await asyncio.sleep(seconds)
    del gm.games[uid]