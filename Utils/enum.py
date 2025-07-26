from enum import Enum


class TCategory(str, Enum):
    FOOD = "Food"
    SHOPPING = "Shopping"
    TRANSPORTATION = "Transportation"
    ENTERTAINMENT = "Entertainment"
    HEALTH = "Health"

class TrendIndicator(str, Enum):
    NEW = "New"
    INC = "Increased"
    DEC = "Decreased"
    STABLE = "Stable"
    STOP = "Stopped"

class SpendIndicator(str, Enum):
    GREEN = "Green"
    ORANGE = "Orange"
    RED = "Red"