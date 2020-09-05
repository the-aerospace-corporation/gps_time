import pytest

from gps_time.core import GPSTime
from gps_time import utilities


def test_arange_gps_time():
    gps_time = GPSTime(0, 0)
    gps_times = utilities.arange_gpstime(gps_time, 1, 1)
    for i, t in enumerate(gps_times):
        assert t == gps_time + i * 0.001


def test_validate_gps_week():
    full_week = 2000
    week = 2000 % 1024
    bad_week = (2000 % 1024) - 1
    utilities.validate_gps_week(full_week, week)
    with pytest.raises(ValueError):
        utilities.validate_gps_week(full_week, bad_week)
