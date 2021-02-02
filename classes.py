from dataclasses import dataclass

from typing import Union


@dataclass
class GameOptions:
    ai_is_white: bool = False
    ai_diff: int = 10
