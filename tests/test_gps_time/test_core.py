import pytest

import datetime
import numpy as np
import ruamel.yaml

from gps_time.core import GPSTime
from gps_time.datetime import datetime2tow


def test_GPSTime_constructor():
    """Test the GPSTime constructor.

    Verifies that the constructor correctly initializes the week number and
    time of week, handling week rollovers if seconds > 604800.
    """
    t = GPSTime(1500, 604799)
    assert t.week_number == 1500, "Weeknum not properly calculated"
    assert t.time_of_week == 604799, "Tow not properly calculated"
    t = GPSTime(1500, 604800)
    assert t.week_number == 1501, "Weeknum not properly calculated"
    assert t.time_of_week == 0, "Tow not properly calculated"


def test_GPSTime_constructor_input_arguments():
    """Test the GPSTime constructor with various input arguments.

    Verifies that the constructor handles different combinations of positional
    and keyword arguments (seconds, femtoseconds, time_of_week) correctly.
    """
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

    t = GPSTime(week_number=1500, time_of_week=604799.9)
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
    """Test conversion from GPSTime to datetime.

    Verifies that a GPSTime object converts correctly to a Python datetime object.
    """
    dt = datetime.datetime(2020, 4, 24, tzinfo=datetime.timezone.utc)
    week, tow = datetime2tow(dt)
    t = GPSTime(week, tow)
    assert t.to_datetime() == dt


def test_GPSTime_from_datetime():
    """Test creation of GPSTime from datetime.

    Verifies that a GPSTime object can be correctly instantiated from a Python
    datetime object, preserving precision where applicable.
    """
    dt = datetime.datetime(2020, 4, 24, tzinfo=datetime.timezone.utc)
    t = GPSTime.from_datetime(dt)
    assert t.to_datetime() == dt
    assert hasattr(t, "seconds"), "from_datetime() did not instantiate seconds"
    assert hasattr(
        t, "femtoseconds"
    ), "from_datetime() did not instantiate femtoseconds"


def test_GPSTime_from_yaml():
    """Test GPSTime serialization/deserialization with YAML.

    Verifies that GPSTime objects can be loaded from YAML, supporting both
    current and legacy formats.
    """
    yaml = ruamel.yaml.YAML()
    yaml.register_class(GPSTime)

    current_yaml_format = """
        !GPSTime
            femtoseconds: 200000000000000
            seconds: 23234
            week_number: 213
        """
    current_format: GPSTime = yaml.load(current_yaml_format)

    assert isinstance(current_format, GPSTime)
    assert hasattr(current_format, "week_number")
    assert hasattr(current_format, "seconds")
    assert hasattr(current_format, "femtoseconds")
    assert current_format.week_number == 213
    assert current_format.seconds == 23234
    assert current_format.femtoseconds == 200000000000000
    assert current_format.time_of_week == 23234.2

    legacy_yaml_format = """
        !GPSTime
            time_of_week: 23234.2
            week_number: 213
        """
    legacy_format: GPSTime = yaml.load(legacy_yaml_format)
    assert isinstance(legacy_format, GPSTime)
    assert hasattr(legacy_format, "week_number")
    assert hasattr(legacy_format, "seconds")
    assert hasattr(legacy_format, "femtoseconds")
    assert legacy_format.week_number == 213
    assert legacy_format.seconds == 23234
    assert np.isclose(legacy_format.femtoseconds, 200000000000000)
    assert legacy_format.time_of_week == 23234.2


@pytest.mark.parametrize(
    "invalid_type", [True, [1], (1,), {1: 1}, 1, 1.0, type, GPSTime(0, 0)]
)
def test_GPSTime_from_datetime_invalid_type(invalid_type):
    """Test error handling for invalid types in from_datetime.

    Verifies that TypeError is raised when input is not a datetime object.
    """
    with pytest.raises(TypeError):
        GPSTime.from_datetime(invalid_type)


def test_GPSTime_to_zcount():
    """Test Z-count conversion.

    Verifies that the Z-count (time of week / 1.5) calculation is correct.
    """
    tow = 500000
    t = GPSTime(10, tow)
    assert t.to_zcount() == t.time_of_week / 1.5


def test_GPSTime_add_float():
    """Test adding a float (seconds) to GPSTime.

    Verifies that adding seconds correctly updates time of week and week number.
    """
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
    """Test adding a timedelta to GPSTime.

    Verifies that adding a datetime.timedelta correctly updates the GPSTime.
    """
    gps_time = GPSTime(2080, 604700)
    gps_time2 = gps_time + datetime.timedelta(seconds=5)
    assert gps_time2.week_number == 2080
    assert gps_time2.time_of_week == 604705
    gps_time2 = gps_time + datetime.timedelta(seconds=100)
    assert gps_time2.week_number == 2081
    assert gps_time2.time_of_week == 0


def test_GPSTime_add_datetime():
    """Test adding a datetime to GPSTime.

    Verifies correct addition behavior when adding a datetime object (converted to GPSTime).
    """
    gps_time = GPSTime(0, 0)
    dt = GPSTime(1920, 415000).to_datetime()
    gps_time_adding = GPSTime.from_datetime(dt)
    gps_time2 = gps_time + dt
    assert gps_time2.week_number == gps_time_adding.week_number
    assert gps_time2.time_of_week == gps_time_adding.time_of_week


def test_GPSTime_add_GPSTime():
    """Test adding two GPSTime objects.

    Verifies that adding two GPSTime objects results in a correct summed GPSTime.
    """
    gps_time = GPSTime(0, 0)
    gps_time_adding = GPSTime(1920, 415000)
    gps_time2 = gps_time + gps_time_adding
    assert gps_time2.week_number == gps_time_adding.week_number
    assert gps_time2.time_of_week == gps_time_adding.time_of_week


def test_GPSTime_add_numpy_array():
    """Test adding a numpy array to GPSTime.

    Verifies element-wise addition when adding a numpy array to a GPSTime object.
    """
    to_add = np.arange(0, 50, 1)
    gps_time = GPSTime(2080, 604700)
    added = gps_time + to_add
    assert len(added) == len(to_add)
    for i, add in enumerate(added):
        assert isinstance(add, GPSTime)
        assert add.time_of_week == gps_time.time_of_week + i


@pytest.mark.parametrize("invalid_type", [True, [1], (1,), {1: 1}])
def test_GPSTime_add_type_error(invalid_type):
    """Test error handling for invalid addition types.

    Verifies that TypeError is raised when adding unsupported types.
    """
    with pytest.raises(TypeError):
        GPSTime(0, 0) + invalid_type


def test_GPSTime_sub_float():
    """Test subtracting a float from GPSTime.

    Verifies correct subtraction of seconds.
    """
    gps_time = GPSTime(2081, 0)
    gps_time2 = gps_time - 1
    assert gps_time2.week_number == 2080
    assert gps_time2.time_of_week == 604799


def test_GPSTime_sub_timedelta():
    """Test subtracting a timedelta from GPSTime.

    Verifies correct subtraction of a datetime.timedelta.
    """
    gps_time = GPSTime(2081, 0)
    gps_time2 = gps_time - datetime.timedelta(seconds=1)
    assert gps_time2.week_number == 2080
    assert gps_time2.time_of_week == 604799


def test_GPSTime_sub_datetime():
    """Test subtracting a datetime from GPSTime.

    Verifies that the result is the difference in seconds (float).
    """
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
    """Test subtracting two GPSTime objects.

    Verifies that the result is the difference in seconds.
    """
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
    """Test subtracting a numpy array of floats from GPSTime.

    Verifies element-wise subtraction.
    """
    arr = np.arange(0, 50, 1)
    gps_time = GPSTime(2080, 100)
    subtracted = gps_time - arr
    for i, t in enumerate(subtracted):
        assert t.time_of_week == 100 - i


def test_GPSTime_sub_nparray_GPSTime():
    """Test subtracting a numpy array of GPSTime objects.

    Verifies element-wise subtraction.
    """
    gps_time = GPSTime(2080, 100)
    arr = np.array([gps_time])
    subtracted = gps_time - arr
    for i, t in enumerate(subtracted):
        assert t == 0


def test_GPSTime_sub_nparray_datetime():
    """Test subtracting a numpy array of datetime objects.

    Verifies element-wise subtraction.
    """
    gps_time = GPSTime(2080, 100)
    arr = np.array([gps_time.to_datetime()])
    subtracted = gps_time - arr
    for i, t in enumerate(subtracted):
        assert t == 0


def test_GPSTime_sub_nparray_timedelta():
    """Test subtracting a numpy array of timedeltas.

    Verifies element-wise subtraction.
    """
    gps_time = GPSTime(2080, 100)
    arr = np.array([datetime.timedelta(seconds=101)])
    subtracted = gps_time - arr
    for i, t in enumerate(subtracted):
        assert t.time_of_week == 604799
        assert t.week_number == 2079


@pytest.mark.parametrize("invalid_type", [True, [1], (1,), {1: 1}])
def test_GPSTime_sub_type_error(invalid_type):
    """Test error handling for invalid subtraction types.

    Verifies TypeError is raised for unsupported types.
    """
    with pytest.raises(TypeError):
        GPSTime(0, 0) - invalid_type


def test_GPSTime_sub_add_picosecond_accuracy():
    """Test picosecond accuracy retention.

    Verifies that small additions/subtractions maintain precision.
    """
    t = GPSTime(1000, 0)
    t2 = t + 1e-12
    assert t2.time_of_week == 1e-12
    t3 = t - 1e-12
    assert t3.week_number == 999
    assert t3.time_of_week == 604800 - 1e-12


@pytest.mark.parametrize(
    "times",
    [
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), True),
        (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12), False),
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000).to_datetime(), True),
        (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12).to_datetime(), False),
    ],
)
def test_GPSTime_less_than(times):
    """Test 'less than' comparison operator."""
    assert (times[0] < times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [True, [1], (1,), {1: 1}, 1, 1.0])
def test_GPSTime_lt_type_error(invalid_type):
    """Test error handling for 'less than' operator."""
    with pytest.raises(TypeError):
        GPSTime(0, 0) < invalid_type


@pytest.mark.parametrize(
    "times",
    [
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), False),
        (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12), True),
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000).to_datetime(), False),
        (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12).to_datetime(), True),
    ],
)
def test_GPSTime_greater_than(times):
    """Test 'greater than' comparison operator."""
    assert (times[0] > times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [True, [1], (1,), {1: 1}, 1, 1.0])
def test_GPSTime_gt_type_error(invalid_type):
    """Test error handling for 'greater than' operator."""
    with pytest.raises(TypeError):
        GPSTime(0, 0) > invalid_type


@pytest.mark.parametrize(
    "times",
    [
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), False),
        (GPSTime(1800, 500000), GPSTime(1800, 500000), True),
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000).to_datetime(), False),
        (GPSTime(1800, 500000), GPSTime(1800, 500000).to_datetime(), True),
    ],
)
def test_GPSTime_equality(times):
    """Test equality operator."""
    assert (times[0] == times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [True, [1], (1,), {1: 1}, 1, 1.0])
def test_GPSTime_eq_type_error(invalid_type):
    """Test error handling for equality operator."""
    with pytest.raises(TypeError):
        GPSTime(0, 0) == invalid_type


@pytest.mark.parametrize("invalid_type", [True, [1], (1,), {1: 1}, 1, 1.0])
def test_GPSTime_ne_type_error(invalid_type):
    """Test error handling for inequality operator."""
    with pytest.raises(TypeError):
        GPSTime(0, 0) != invalid_type


@pytest.mark.parametrize(
    "times",
    [
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), True),
        (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12), False),
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000).to_datetime(), True),
        (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12).to_datetime(), False),
        (GPSTime(1800, 500000), GPSTime(1800, 500000), True),
        (GPSTime(1800, 500000), GPSTime(1800, 500000).to_datetime(), True),
        (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12), False),
        (GPSTime(1800, 500000), GPSTime(1800, 499999 + 1e-12).to_datetime(), False),
    ],
)
def test_GPSTime_less_than_equal(times):
    """Test 'less than or equal' comparison operator."""
    assert (times[0] <= times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [True, [1], (1,), {1: 1}, 1, 1.0])
def test_GPSTime_le_type_error(invalid_type):
    """Test error handling for 'less than or equal' operator."""
    with pytest.raises(TypeError):
        GPSTime(0, 0) <= invalid_type


@pytest.mark.parametrize(
    "times",
    [
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), False),
        (GPSTime(1800, 500000), GPSTime(1800, 500000), True),
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000).to_datetime(), False),
        (GPSTime(1800, 500000), GPSTime(1800, 500000).to_datetime(), True),
        (GPSTime(1800, 500000), GPSTime(1800, 500000), True),
        (GPSTime(1800, 500000), GPSTime(1800, 500000).to_datetime(), True),
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000), False),
        (GPSTime(1800, 499999 + 1e-12), GPSTime(1800, 500000).to_datetime(), False),
    ],
)
def test_GPSTime_greater_than_equal(times):
    """Test 'greater than or equal' comparison operator."""
    assert (times[0] >= times[1]) == times[2]


@pytest.mark.parametrize("invalid_type", [True, [1], (1,), {1: 1}, 1, 1.0])
def test_GPSTime_ge_type_error(invalid_type):
    """Test error handling for 'greater than or equal' operator."""
    with pytest.raises(TypeError):
        GPSTime(0, 0) <= invalid_type


def test_GPSTime_iadd():
    """Test in-place addition (+=)."""
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
    """Test in-place subtraction (-=)."""
    gps_time = GPSTime(2080, 604800)
    gps_time -= 5
    assert gps_time.week_number == 2080
    assert gps_time.time_of_week == 604795


def test_has_repr():
    """Test __repr__ method."""
    repr(GPSTime(2080, 604800))


def test_has_hash():
    """Test __hash__ method."""
    GPSTime(2080, 604800).__hash__()