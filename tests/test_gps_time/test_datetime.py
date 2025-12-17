import pytest

import datetime
import numpy as np

from typing import Tuple

import gps_time.datetime as time
from gps_time.core import GPSTime


@pytest.mark.parametrize("tow,date", [
    ((0, 0), datetime.datetime(1980, 1, 6, tzinfo=datetime.timezone.utc)),
    ((1000, 0), datetime.datetime(1999, 3, 7, tzinfo=datetime.timezone.utc)),
    ((2082, 1052.5), datetime.datetime(2019, 12, 1, 0, 17, 32, 500000, tzinfo=datetime.timezone.utc)),
    ((1500, 604799), datetime.datetime(2008, 10, 11, 23, 59, 59, tzinfo=datetime.timezone.utc)),
    ((1500, 604800), datetime.datetime(2008, 10, 12, tzinfo=datetime.timezone.utc)),
])
def test_tow2datetime(tow: Tuple[int, float], date: datetime.datetime):
    """Test proper conversion over several corner cases

    Parameters
    ----------
    tow : Tuple[int, float]
        weeknum, tow
    date : datetime.datetime
        Date it should return
    """
    tow = time.tow2datetime(*tow)
    assert tow == date, f"Did not produce correct datetime {tow} != {date}"


@pytest.mark.parametrize("date,tow", [
    (datetime.datetime(1980, 1, 6, tzinfo=datetime.timezone.utc), (0, 0)),
    (datetime.datetime(1999, 3, 7, tzinfo=datetime.timezone.utc), (1000, 0)),
    (datetime.datetime(2019, 12, 1, 0, 17, 32, 500000, tzinfo=datetime.timezone.utc), (2082, 1052.5)),
    (datetime.datetime(2008, 10, 11, 23, 59, 59, tzinfo=datetime.timezone.utc), (1500, 604799)),
    (datetime.datetime(2008, 10, 12, tzinfo=datetime.timezone.utc), (1501, 0)),
])
def test_datetime2tow(date: datetime.datetime, tow: Tuple[int, float]):
    """Test proper conversion over several corner cases

    Parameters
    ----------
    tow : Tuple[int, float]
        weeknum, tow
    date : datetime.datetime
        Date it should return
    """
    tow2 = time.datetime2tow(date)
    assert tow == tow2, f"Did not produce correct tow {tow} != {tow2}"


def test_datetime2tow_argerror():
    """Test argument error for datetime2tow.

    Verifies TypeError when passing invalid arguments (non-datetime).
    """
    with pytest.raises(TypeError):
        time.datetime2tow(1, 1)

def test_arange_datetime():
    """Test arange_datetime utility.

    Verifies that it creates a correct range of datetime objects.
    """
    gps_time = GPSTime(0, 0).to_datetime()
    gps_times = time.arange_datetime(gps_time, 1, 1)
    for i, t in enumerate(gps_times):
        assert t == gps_time + datetime.timedelta(seconds=i * 0.001)

@pytest.mark.parametrize("invalid_type", [
    "1", 1.0, True
])
def testcorrect_week_year_error(invalid_type):
    """Test error handling for correct_week with invalid year types."""
    with pytest.raises(ValueError):
        time.correct_week(0, 0, invalid_type)
    time.correct_week(0, 0, 1980)


def testcorrect_week_inconsistent_error():
    """Test logic for correct_week consistency check.

    Verifies ValueError if week number is inconsistent with the provided year.
    """
    time.correct_week(0, 0, 1980)
    with pytest.raises(ValueError):
        time.correct_week(0, 0, 1979)
    time.correct_week(-1, 0, 1979)


def test_tow2datetime():
    """Test basic tow2datetime conversion."""
    dt1 = time.tow2datetime(0, 0)
    assert dt1 == datetime.datetime(1980, 1, 6, tzinfo=datetime.timezone.utc)
    dt2 = time.tow2datetime(0, 1000, 2019)


@pytest.mark.parametrize("invalid_type", [
    "1", 1.0, True, [1], (1,), {1: 1}, np.array([5]),
    np.array([datetime.datetime(2019, 1, 1)])
])
def test_datetime2tow_TypeError(invalid_type):
    """Test TypeError on invalid inputs for datetime2tow."""
    with pytest.raises(TypeError):
        time.datetime2tow(invalid_type)

def test_tow2zcount():
    """Test tow2zcount conversion."""
    zcount = time.tow2zcount(0, 0, 1980)
    assert zcount == (0, 0)
    zcount = time.tow2zcount(0, 6, 1980)
    assert zcount == (0, 4)


def test_zcount2tow():
    """Test zcount2tow conversion."""
    zcount = time.zcount2tow(0, 0, 1980)
    assert zcount == (0, 0)
    zcount = time.zcount2tow(0, 4, 1980)
    assert zcount == (0, 6)


def test_datetime2zcount():
    """Test datetime2zcount conversion."""
    date = datetime.datetime(1980, 1, 6, 0, 0, 0, tzinfo=datetime.timezone.utc)
    zcount = time.datetime2zcount(date)
    assert(zcount == (0, 0))
    zcount = time.datetime2zcount(date + datetime.timedelta(seconds=6))
    assert(zcount == (0, 4))
    zcount = time.datetime2zcount(date + datetime.timedelta(seconds=604800))
    assert(zcount == (1, 0))


def test_zcount2datetime():
    """Test zcount2datetime conversion."""
    date = datetime.datetime(1980, 1, 6, 0, 0, 0, tzinfo=datetime.timezone.utc)
    zcount = time.zcount2datetime(0, 0, 1980)
    assert(zcount == date)
    zcount = time.zcount2datetime(0, 4, 1980)
    assert zcount == date + datetime.timedelta(seconds=6)
    zcount = time.zcount2datetime(0, 604800 / 1.5, 1980)
    assert zcount == date + datetime.timedelta(seconds=604800)