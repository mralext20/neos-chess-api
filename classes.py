from dataclasses import dataclass
from typing import Optional
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
