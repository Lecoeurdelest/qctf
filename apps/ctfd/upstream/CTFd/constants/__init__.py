from enum import Enum


class RawEnum(Enum):
    """
    This is a customized enum class which should be used with a mixin.
    The mixin should define the types of each member.

    For example:

    class Colors(str, RawEnum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"
    """

    def __str__(self):
        return str(self._value_)

    @classmethod
    def keys(cls):
        return list(cls.__members__.keys())

    @classmethod
    def values(cls):
        return list(cls.__members__.values())

    @classmethod
    def test(cls, value):
        try:
            return bool(cls(value))
        except ValueError:
            return False
