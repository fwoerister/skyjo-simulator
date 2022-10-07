from enum import Enum

CARD_FREQUENCIES = {
    -2: 5,
    -1: 15,
    0: 15,
    1: 10,
    2: 10,
    3: 10,
    4: 10,
    5: 10,
    6: 10,
    7: 10,
    8: 10,
    9: 10,
    10: 10,
    11: 10,
    12: 10,
}


class DRAW_LOCATION(Enum):
    DRAW_STACK = 1,
    DISCARD_STACK = 2,
