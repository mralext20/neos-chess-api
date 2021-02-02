from classes import GameOptions
from stockfish import Stockfish
from Chessnut import Game as Game
from typing import Dict
from dataclasses import dataclass
import asyncio
from functools import partial


@dataclass
class ChessGame:
    in_use = asyncio.Lock()
    game: Game = Game()
    against_computer: bool = True
    opts: GameOptions = GameOptions()


class GameManager:
    games: Dict[str, ChessGame] = {}
    stockfish = Stockfish("./bin/stockfish")
    stockfish_lock = asyncio.Lock()

    def start_game(
        self, uid: str, opts: GameOptions, use_stockfish: bool = True
    ) -> ChessGame:
        if not use_stockfish:
            raise NotImplementedError(
                "not using stockfish is not currently implimented"
            )
        self.games[uid] = ChessGame()
        return self.games[uid]

    async def make_move(self, id: str, move: str) -> bool:
        """
        returns weather the move was made or not (i.e. if the move is valid)
        """
        game = self.games[id]
        if move not in game.get_moves():
            return False
        game.apply_move(move)
        return await self._do_ai_move(id)

    def get_game(self, id: str) -> ChessGame:
        return self.games[id]

    async def _do_ai_move(self, id: str) -> str:
        """
        has the AI do a move, then returns it.
        """
        game = self.games[id]
        async with self.stockfish_lock:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                partial(self.stockfish.set_fen_position, game.game.get_fen())
            )
            move = await loop.run_in_executor(self.stockfish.get_best_move_time)
        game.game.apply_move(move)
        return move
