from enum import Enum

# Using enums to keep the name of the user and system constant in db and usage
# Better to use enums than to use string literals


class Source(Enum):
    User = "user"
    System = "system"
    Assistant = "assistant"
