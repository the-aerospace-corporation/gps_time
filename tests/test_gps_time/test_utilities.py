import pytest

from gps_time.core import GPSTime
from gps_time import utilities


def test_arange_gps_time():
    """Test arange_gpstime utility.

    Verifies that it creates a sequence of GPSTime objects with correct spacing.
    """
    gps_time = GPSTime(0, 0)
    gps_times = utilities.arange_gpstime(gps_time, 1, 1)
    for i, t in enumerate(gps_times):
        assert t == gps_time + i * 0.001


def test_validate_gps_week():
    """Test validate_gps_week utility.

    Verifies that it raises ValueError when the mod 1024 week number is
    inconsistent with the full week number.
    """
    full_week = 2000
    week = 2000 % 1024
    bad_week = (2000 % 1024) - 1
    utilities.validate_gps_week(full_week, week)
    with pytest.raises(ValueError):
        utilities.validate_gps_week(full_week, bad_week)
