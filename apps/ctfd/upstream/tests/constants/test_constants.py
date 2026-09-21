from CTFd.constants import RawEnum


def test_RawEnum():
    class Colors(str, RawEnum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    class Numbers(str, RawEnum):
        ONE = 1
        TWO = 2
        THREE = 3

    assert Colors.RED == "red"
    assert Colors.GREEN == "green"
    assert Colors.BLUE == "blue"
    assert Colors.test("red") is True
    assert Colors.test("purple") is False
    assert str(Numbers.ONE) == "1"
    assert sorted(Colors.keys()) == sorted(["RED", "GREEN", "BLUE"])
    assert sorted(Colors.values()) == sorted(["red", "green", "blue"])
