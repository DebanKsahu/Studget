from enum import Enum


class TCategory(str, Enum):
    FOOD = "Food"
    SHOPPING = "Shopping"
    TRANSPORTATION = "Transportation"
    ENTERTAINMENT = "Entertainment"
    HEALTH = "Health"