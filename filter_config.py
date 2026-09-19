from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    NO = 0
    RED = 1
    ORANGE = 2
    YELLOW = 3
    GREEN = 4
    CYAN = 5
    BLUE = 6
    MAGENTA = 7
    CUSTOM = 8


@dataclass
class FilterConfig:
    blur_kernel: int = 0
    sigma: float = 1
    history_size: int = 1
    power: float = 1
    grayscale: bool = False
    invert_colors: bool = False
    color: Color = Color.NO
    custom_color: tuple[int, int, int] = (255, 255, 255)
    color_threshold: int = 0
    invert_color_threshold: bool = False
