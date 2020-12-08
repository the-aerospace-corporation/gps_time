import pytest

import datetime
import numpy as np

from gps_time.core import GPSTime
from gps_time.datetime import datetime2tow


def test_GPSTime_constructor():
    t = GPSTime(1500, 604799)
    assert t.week_number == 1500, "Weeknum not properly calculated"
    assert t.time_of_week == 604799, "Tow not properly calculated"
    t = GPSTime(1500, 604800)
    assert t.week_number == 1501, "Weeknum not properly calculated"
    assert t.time_of_week == 0, "Tow not properly calculated"

def test_GPSTime_constructor_input_arguments():
    t = GPSTime(1500, 604799, 9e14)
    assert t.week_number == 1500, "Weeknum not properly calculated"
    assert t.time_of_week == 604799.9, "Tow not properly calculated"
    assert t.seconds == 604799, "seconds not properly calculated"
    assert t.femtoseconds == 9e14, "femtoseconds not properly calculated"

    # Loses femtosecond accuracy
    t = GPSTime(1500, 604799.9)
    assert t.week_number == 1500, "Weeknum not properly calculated"
    assert t.time_of_week == 604799.9, "Tow not properly calculated"
    assert t.seconds == 604799, "seconds not properly calculated"
    assert np.isclose(t.femtoseconds, 9e14), "femtoseconds not properly calculated"

    t = GPSTime(1500, seconds=604799, femtoseconds=9e14)
    assert t.week_number == 1500, "Weeknum not properly calculated"
    assert t.time_of_week == 604799.9, "Tow not properly calculated"
    assert t.seconds == 604799, "seconds not properly calculated"
    assert t.femtoseconds == 9e14, "femtoseconds not properly calculated"


    t = GPSTime(1500, femtoseconds=9e14, seconds=604799)
    assert t.week_number == 1500, "Weeknum not properly calculated"
    assert t.time_of_week == 604799.9, "Tow not properly calculated"
    assert t.seconds == 604799, "seconds not properly calculated"
    assert t.femtoseconds == 9e14, "femtoseconds not properly calculated"

    # These will not produce accurate results at the femtosecond level
    t = GPSTime(1500, seconds=604799.9)
    assert t.week_number == 1500, "Weeknum not properly calculated"
    assert t.time_of_week == 604799.9, "Tow not properly calculated"
    assert t.seconds == 604799, "seconds not properly calculated"
    assert np.isclose(t.femtoseconds, 9e14), "femtoseconds not properly calculated"

    t = GPSTime(1500, time_of_week=604799.9)
    assert t.week_number == 1500, "Weeknum not properly calculated"
    assert t.time_of_week == 604799.9, "Tow not properly calculated"
    assert t.seconds == 604799, "seconds not properly calculated"
    assert np.isclose(t.femtoseconds, 9e14), "femtoseconds not properly calculated"

    with pytest.raises(ValueError):
       t = GPSTime(1500, 1, 2, 3)
    

    with pytest.raises(ValueError):
       t = GPSTime(1500, time_of_week=1.0, seconds=2, femtoseconds=3)

    with pytest.raises(ValueError):
        t = GPSTime(1500, time_of_week=604799, femtoseconds=9e14)


def test_GPSTime_to_datetime():
    dt = datetime.datetime(2020, 4, 24)
    week, tow = datetime2tow(dt)
    t = GPSTime(week, tow)
    assert t.to_datetime() == dt


def test_GPSTime_from_datetime():
    dt = datetime.datetime(2020, 4, 24)
    t = GPSTime.from_datetime(dt)
    assert t.to_datetime() == dt


@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}, 1, 1.0, type, GPSTime(0, 0)
])
def test_GPSTime_from_datetime_invalid_type(invalid_type):
    with pytest.raises(TypeError):
        GPSTime.from_datetime(invalid_type)


def test_GPSTime_to_zcount():
    tow = 500000
    t = GPSTime(10, tow)
    assert t.to_zcount() == t.time_of_week / 1.5


def test_GPSTime_add_float():
    gps_time = GPSTime(2080, 604700)
    gps_time2 = gps_time + 5
    assert gps_time2.week_number == 2080
    assert gps_time2.time_of_week == 604705
    gps_time2 = gps_time + 100
    assert gps_time2.week_number == 2081
    assert gps_time2.time_of_week == 0
    gps_time2 = gps_time + -604701
    assert gps_time2.week_number == 2079
    assert gps_time2.time_of_week == 604799



def test_GPSTime_add_timedelta():
    gps_time = GPSTime(2080, 604700)
    gps_time2 = gps_time + datetime.timedelta(seconds=5)
    assert gps_time2.week_number == 2080
    assert gps_time2.time_of_week == 604705
    gps_time2 = gps_time + datetime.timedelta(seconds=100)
    assert gps_time2.week_number == 2081
    assert gps_time2.time_of_week == 0


def test_GPSTime_add_datetime():
    gps_time = GPSTime(0, 0)
    dt = GPSTime(1920, 415000).to_datetime()
    gps_time_adding = GPSTime.from_datetime(dt)
    gps_time2 = gps_time + dt
    assert gps_time2.week_number == gps_time_adding.week_number
    assert gps_time2.time_of_week == gps_time_adding.time_of_week


def test_GPSTime_add_GPSTime():
    gps_time = GPSTime(0, 0)
    gps_time_adding = GPSTime(1920, 415000)
    gps_time2 = gps_time + gps_time_adding
    assert gps_time2.week_number == gps_time_adding.week_number
    assert gps_time2.time_of_week == gps_time_adding.time_of_week


def test_GPSTime_add_numpy_array():
    to_add = np.arange(0, 50, 1)
    gps_time = GPSTime(2080, 604700)
    added = gps_time + to_add
    assert len(added) == len(to_add)
    for i, add in enumerate(added):
        assert isinstance(add, GPSTime)
        assert add.time_of_week == gps_time.time_of_week + i


@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}
])
def test_GPSTime_add_type_error(invalid_type):
    with pytest.raises(TypeError):
        GPSTime(0, 0) + invalid_type


def test_GPSTime_sub_float():
    gps_time = GPSTime(2081, 0)
    gps_time2 = gps_time - 1
    assert gps_time2.week_number == 2080
    assert gps_time2.time_of_week == 604799


def test_GPSTime_sub_timedelta():
    gps_time = GPSTime(2081, 0)
    gps_time2 = gps_time - datetime.timedelta(seconds=1)
    assert gps_time2.week_number == 2080
    assert gps_time2.time_of_week == 604799


def test_GPSTime_sub_datetime():
    gps_time = GPSTime(2080, 0)
    dt = gps_time.to_datetime()
    gps_time2 = gps_time - dt
    assert gps_time2 == 0
    gps_time3 = GPSTime(2080, 5)
    dt = gps_time3.to_datetime()
    gps_time2 = gps_time - dt
    assert gps_time2 == -5
    gps_time4 = GPSTime(2079, 604795)
    dt = gps_time4.to_datetime()
    gps_time2 = gps_time - dt
    assert gps_time2 == 5


def test_GPSTime_sub_GPSTime():
    gps_time = GPSTime(2080, 0)
    gps_time2 = gps_time - gps_time
    assert gps_time2 == 0
    gps_time3 = GPSTime(2080, 5)
    gps_time2 = gps_time - gps_time3
    assert gps_time2 == -5
    gps_time4 = GPSTime(2079, 604795)
    gps_time2 = gps_time - gps_time4
    assert gps_time2 == 5


def test_GPSTime_sub_nparray_float():
    arr = np.arange(0, 50, 1)
    gps_time = GPSTime(2080, 100)
    subtracted = gps_time - arr
    for i, t in enumerate(subtracted):
        assert t.time_of_week == 100 - i


def test_GPSTime_sub_nparray_GPSTime():
    gps_time = GPSTime(2080, 100)
    arr = np.array([gps_time])
    subtracted = gps_time - arr
    for i, t in enumerate(subtracted):
        assert t == 0

def test_GPSTime_sub_nparray_datetime():
    gps_time = GPSTime(2080, 100)
    arr = np.array([gps_time.to_datetime()])
    subtracted = gps_time - arr
    for i, t in enumerate(subtracted):
        assert t == 0


def test_GPSTime_sub_nparray_timedelta():
    gps_time = GPSTime(2080, 100)
    arr = np.array([datetime.timedelta(seconds=101)])
    subtracted = gps_time - arr
    for i, t in enumerate(subtracted):
        assert t.time_of_week == 604799
        assert t.week_number == 2079


@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}
])
def test_GPSTime_sub_type_error(invalid_type):
    with pytest.raises(TypeError):
        GPSTime(0, 0) - invalid_type


def test_GPSTime_sub_add_picosecond_accuracy():
    t = GPSTime(1000, 0)
    t2 = t + 1e-12
    assert t2.time_of_week == 1e-12
    t3 = t - 1e-12
    assert t3.week_number == 999
    assert t3.time_of_week == 604800 - 1e-12


@pytest.mark.parametrize("times", [
    (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), True),
    (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12), False),
    (GPSTime(1800, 499999 + 1e-12),
        GPSTime(1800, 500000).to_datetime(), True),
    (GPSTime(1800, 500000),
        GPSTime(1800, 499999 + 1e-12).to_datetime(), False)
])
def test_GPSTime_less_than(times):
    assert (times[0] < times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}, 1, 1.0
])
def test_GPSTime_lt_type_error(invalid_type):
    with pytest.raises(TypeError):
        GPSTime(0, 0) < invalid_type


@pytest.mark.parametrize("times", [
    (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), False),
    (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12), True),
    (GPSTime(1800, 499999 + 1e-12),
        GPSTime(1800, 500000).to_datetime(), False),
    (GPSTime(1800, 500000),
        GPSTime(1800, 499999 + 1e-12).to_datetime(), True)
])
def test_GPSTime_greater_than(times):
    assert (times[0] > times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}, 1, 1.0
])
def test_GPSTime_gt_type_error(invalid_type):
    with pytest.raises(TypeError):
        GPSTime(0, 0) > invalid_type


@pytest.mark.parametrize("times", [
    (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), False),
    (GPSTime(1800, 500000), GPSTime(1800, 500000), True),
    (GPSTime(1800, 499999 + 1e-12),
        GPSTime(1800, 500000).to_datetime(), False),
    (GPSTime(1800, 500000),
        GPSTime(1800, 500000).to_datetime(), True),
])
def test_GPSTime_equality(times):
    assert (times[0] == times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}, 1, 1.0
])
def test_GPSTime_eq_type_error(invalid_type):
    with pytest.raises(TypeError):
        GPSTime(0, 0) == invalid_type

@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}, 1, 1.0
])
def test_GPSTime_ne_type_error(invalid_type):
    with pytest.raises(TypeError):
        GPSTime(0, 0) != invalid_type

@pytest.mark.parametrize("times", [
    (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), True),
    (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12), False),
    (GPSTime(1800, 499999 + 1e-12),
        GPSTime(1800, 500000).to_datetime(), True),
    (GPSTime(1800, 500000),
        GPSTime(1800, 499999 + 1e-12).to_datetime(), False),
    (GPSTime(1800, 500000), GPSTime(1800, 500000), True),
    (GPSTime(1800, 500000),
        GPSTime(1800, 500000).to_datetime(), True),
    (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12), False),
    (GPSTime(1800, 500000),
        GPSTime(1800, 499999 + 1e-12).to_datetime(), False)
])
def test_GPSTime_less_than_equal(times):
    assert (times[0] <= times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}, 1, 1.0
])
def test_GPSTime_le_type_error(invalid_type):
    with pytest.raises(TypeError):
        GPSTime(0, 0) <= invalid_type


@pytest.mark.parametrize("times", [
    (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), False),
    (GPSTime(1800, 500000), GPSTime(1800, 500000), True),
    (GPSTime(1800, 499999 + 1e-12),
        GPSTime(1800, 500000).to_datetime(), False),
    (GPSTime(1800, 500000),
        GPSTime(1800, 500000).to_datetime(), True),
    (GPSTime(1800, 500000), GPSTime(1800, 500000), True),
    (GPSTime(1800, 500000),
        GPSTime(1800, 500000).to_datetime(), True),
    (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), False),
    (GPSTime(1800, 499999 + 1e-12),
        GPSTime(1800, 500000).to_datetime(), False),
])
def test_GPSTime_greater_than_equal(times):
    assert (times[0] >= times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [
    True, [1], (1,), {1: 1}, 1, 1.0
])
def test_GPSTime_ge_type_error(invalid_type):
    with pytest.raises(TypeError):
        GPSTime(0, 0) <= invalid_type


def test_GPSTime_iadd():
    gps_time = GPSTime(2080, 604700)
    gps_time += 5
    assert gps_time.week_number == 2080
    assert gps_time.time_of_week == 604705
    gps_time += 95
    assert gps_time.week_number == 2081
    assert gps_time.time_of_week == 0
    gps_time += -100
    assert gps_time.week_number == 2080
    assert gps_time.time_of_week == 604700


def test_GPSTime_isub():
    gps_time = GPSTime(2080, 604800)
    gps_time -= 5
    assert gps_time.week_number == 2080
    assert gps_time.time_of_week == 604795


def test_has_repr():
    repr(GPSTime(2080, 604800))

def test_has_hash():
    GPSTime(2080, 604800).__hash__()