import asyncio
import sys
from functools import partial
from typing import Dict, Optional
from uuid import UUID

from stockfish import Stockfish

from classes import ChessGame, GameOptions, delete_match_in


class GameManager:
    def __init__(self) -> None:
        self.path = "stockfish.exe" if sys.platform == "win32" else "stockfish"
        try:
            Stockfish(self.path)
        except FileNotFoundError:
            print(f"cannot find stockfish executable. try putting one as `{self.path}` in the path")
            exit(-1)

    games: Dict[UUID, ChessGame] = {}

    def start_game(self, uid: UUID, opts: GameOptions) -> ChessGame:
        if opts.ai_is_white is None:
            raise NotImplementedError("not using stockfish is not currently implimented")
        self.games[uid] = ChessGame(
            stockfish=Stockfish(self.path), timer=asyncio.get_event_loop().create_task(delete_match_in(self, uid))
        )
        return self.games[uid]

    async def make_move(self, uid: UUID, move: str) -> Optional[str]:
        """
        returns the move the computer makes in response, or None if against another player.
        raises InvalidMove when the move is Invalid.
        """
        game = self.games[uid]
        game.timer.cancel()
        game.timer = asyncio.get_event_loop().create_task(delete_match_in(self, uid))
        game.game.apply_move(move)
        if game.game.status == game.game.CHECKMATE or game.game.status == game.game.STALEMATE:
            del self.games[uid]
            return

        if game.opts.ai_is_white is not None:
            ai_move = await self.do_ai_move(uid)
            if game.game.status == game.game.CHECKMATE or game.game.status == game.game.STALEMATE:
                del self.games[uid]
            return ai_move

    async def do_ai_move(self, id: UUID) -> str:
        """
        has the AI do a move, applying it, then returns it.
        """
        game = self.games[id]
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, partial(game.stockfish.set_fen_position, game.game.get_fen()))
        await loop.run_in_executor(None, partial(game.stockfish.set_skill_level, game.opts.ai_diff))
        move = await loop.run_in_executor(None, game.stockfish.get_best_move_time)
        game.game.apply_move(move)
        return move
