import asyncio
from functools import partial
from typing import Dict, Optional
from uuid import UUID
from stockfish import Stockfish
import stockfish
import sys
from classes import ChessGame, GameOptions


class GameManager:
    def __init__(self) -> None:
        path = "stockfish.exe" if sys.platform == "win32" else "stockfish"
        try:
            self.stockfish = Stockfish(path)
        except FileNotFoundError:
            print(f"cannot find stockfish executable. try putting one as `{path}` in the path")
            exit(-1)

    games: Dict[UUID, ChessGame] = {}
    stockfish_lock = asyncio.Lock()

    def start_game(self, uid: UUID, opts: GameOptions) -> ChessGame:
        if opts.ai_is_white is None:
            raise NotImplementedError("not using stockfish is not currently implimented")
        self.games[uid] = ChessGame()
        return self.games[uid]

    async def make_move(self, uid: UUID, move: str) -> Optional[str]:
        """
        returns the move the computer makes in response, or None if against another player.
        raises InvalidMove when the move is Invalid.
        """
        game = self.games[uid]
        game.game.apply_move(move)
        if game.game.status == game.game.CHECKMATE or game.game.status == game.game.STALEMATE:
            del self.games[uid]
            return

        if game.opts.ai_is_white is not None:
            move = await self.do_ai_move(uid)
            if game.game.status == game.game.CHECKMATE or game.game.status == game.game.STALEMATE:
                del self.games[uid]
            return move

    async def do_ai_move(self, id: UUID) -> str:
        """
        has the AI do a move, applying it, then returns it.
        """
        game = self.games[id]
        async with self.stockfish_lock:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, partial(self.stockfish.set_fen_position, game.game.get_fen()))
            await loop.run_in_executor(None, partial(self.stockfish.set_skill_level, game.opts.ai_diff))
            move = await loop.run_in_executor(None, self.stockfish.get_best_move_time)
        game.game.apply_move(move)
        return move
