import pytest

import datetime

from gps_time.core import GPSTime
from gps_time.leapseconds import LeapSeconds


@pytest.mark.parametrize("year,leap_seconds", [
    (1981, 0), (1982, 1), (1983, 2), (1984, 3), (1986, 4), (1989, 5),
    (1991, 7), (1992, 7), (1993, 8), (1995, 10), (1997, 11), (1998, 12),
    (2000, 13), (2007, 14), (2010, 15), (2013, 16), (2016, 17), (2020, 18),
    (2021, 18)
])
def test_get_leap_seconds(year, leap_seconds):
    """Test retrieval of leap seconds for various years.

    Verifies that the correct number of leap seconds is returned for start of
    given years.
    """
    date = datetime.datetime(year, 1, 1, 0, 0, 0)
    calculated_ls = LeapSeconds.get_leap_seconds(
        GPSTime.from_datetime(date))
    assert leap_seconds == calculated_ls


@pytest.mark.parametrize("year,leap_second_date,leap_second", [
    (1980, GPSTime(77, 259200), 1), (2021, None, None),
    (2000, GPSTime(1356, 0.0), 14)
])
def test_get_next_leap_seconds(year, leap_second_date, leap_second):
    """Test prediction of next leap second.

    Verifies that the next planned leap second is correctly identified
    from a given year.
    """
    date = datetime.datetime(year, 1, 1, 0, 0, 0)
    out = LeapSeconds.get_next_leap_second(
        GPSTime.from_datetime(date))
    if leap_second_date is not None:
        date, calculated_ls = out
        assert leap_second_date == date
        assert leap_second == calculated_ls
    else:
        assert out is None


def test_leap_second_boundaries():
    """Test leap second logic at exact transition boundaries.

    Verifies that the number of leap seconds updates exactly at the
    moment of transition (and not before or after).
    """
    # 1981 Leap Second (June 30)
    # Before
    t = datetime.datetime(1981, 6, 30, 23, 59, 59, tzinfo=datetime.timezone.utc)
    assert LeapSeconds.get_leap_seconds(GPSTime.from_datetime(t)) == 0

    # At transition (Midnight July 1st)
    t = datetime.datetime(1981, 7, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert LeapSeconds.get_leap_seconds(GPSTime.from_datetime(t)) == 1

    # After
    t = datetime.datetime(1981, 7, 1, 0, 0, 0, 1, tzinfo=datetime.timezone.utc)
    assert LeapSeconds.get_leap_seconds(GPSTime.from_datetime(t)) == 1

    # 2016 Leap Second (Dec 31)
    # Before
    t = datetime.datetime(2016, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
    assert LeapSeconds.get_leap_seconds(GPSTime.from_datetime(t)) == 17

    # At transition (Midnight Jan 1st)
    t = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert LeapSeconds.get_leap_seconds(GPSTime.from_datetime(t)) == 18


if __name__ == "__main__":
    gps_time = GPSTime.from_datetime(datetime.datetime(2000, 1, 1))
    # gps_time2 = gps_time + datetime.datetime(1990, 1, 6)
    # GPSTime(0, 0) - 1
    #print(time.tow2zcount(0, 0, 1980))
    # print(LeapSeconds.get_leap_seconds(gps_time))
    date = datetime.datetime(1980, 1, 1, 0, 0, 0)
    calculated_ls = LeapSeconds.get_next_leap_second(gps_time)
    print(calculated_ls)
