from enum import Enum


class Category(Enum):
    """
    Category assigned to the result of a request
    """
    Good = "✅"
    Warning = "😐"
    Error = "🛑"
    Critical = "😬"
    Failed = "⚪"
