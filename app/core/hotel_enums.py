# core/enums.py (or within hotel.py)

from enum import Enum

class StateEnum(str, Enum):
    GUJARAT = "gujarat"
    PUNJAB = "punjab"
    GOA = "goa"

class CountryEnum(str, Enum):
    INDIA = "india"
    USA = "usa"
