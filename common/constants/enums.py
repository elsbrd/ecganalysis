from enum import Enum


class ChoicesEnum(Enum):
    @classmethod
    def choices(cls):
        return [(x.value, x.name.replace("_", " ").title()) for x in cls]
