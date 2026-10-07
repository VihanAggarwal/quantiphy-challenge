import math

import pytest

from qp.data import target_unit
from qp.parse import parse_answer


@pytest.mark.parametrize("text,unit,expected", [
    ("2.5 m", "m", 2.5),
    ("150 cm", "m", 1.5),
    ("1.2 m/s", "cm/s", 120.0),
    ("Final answer: 9.81 m/s^2", "m/s^2", 9.81),
    ("Prior box is 120 px wide.\nFinal answer: 3.4 meters", "m", 3.4),
    ("about 1,086.5 cm", "cm", 1086.5),
    ("2.27×10^3 m", "m", 2270.0),
    ("-4 m/s", "m/s", 4.0),
    ("36 km/h", "m/s", 10.0),
])
def test_parse(text, unit, expected):
    assert parse_answer(text, unit) == pytest.approx(expected)


def test_parse_no_number():
    assert math.isnan(parse_answer("I cannot tell", "m"))


@pytest.mark.parametrize("q,unit", [
    ("What is the height of the person in meters?", "m"),
    ("What is the length of the wood block in cm?", "cm"),
    ("What is the speed of the car in m/s?", "m/s"),
    ("What is the acceleration of the ball in cm/s^2?", "cm/s^2"),
])
def test_target_unit(q, unit):
    assert target_unit(q) == unit
