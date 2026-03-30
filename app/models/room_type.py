from enum import Enum

class RoomType(str, Enum):
    REGULAR = "REGULAR"
    DELUXE = "DELUXE"
    LUXURY = "LUXURY"