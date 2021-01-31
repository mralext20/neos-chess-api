from stockfish import Stockfish
from Chessnut import Game as Game
from typing import Dict
from dataclasses import dataclass


@dataclass
class ChessGame:
    game: Game = Game()
    against_computer: bool = True


class GameManager:
    games: Dict[str, ChessGame] = {}
    stockfish = Stockfish("./bin/stockfish")

    def start_game(id: str, use_stockfish: bool = True) -> ChessGame:
        """"""
        if not use_stockfish:
            raise NotImplementedError(
                "not using stockfish is not currently implimented"
            )
        pass

    def make_move(self, id: str, move: str) -> bool:
        """
        returns weather the move was made or not (i.e. if the move is valid)
        """
        game = self.games[id]
        if move not in game.get_moves():
            return False
        game.apply_move(move)
        pass

    def get_game(self, id: str) -> ChessGame:
        return self.games[id]
