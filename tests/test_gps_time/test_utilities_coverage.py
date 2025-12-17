import pytest
from gps_time.core import GPSTime
from gps_time.utilities import arange_gpstime, validate_gps_week

def test_arange_gpstime():
    """Test arange_gpstime."""
    start = GPSTime(100, 0)
    # Duration 3s, Step 1000ms = 1s. Result: 0, 1, 2. (3 excluded?)
    res = arange_gpstime(start, 3.0, 1000.0)
    assert len(res) == 3
    assert res[0] == start
    assert res[1].seconds == 1
    assert res[2].seconds == 2

def test_validate_gps_week():
    """Test valdiate_gps_week."""
    # Valid
    validate_gps_week(1024 + 5, 5) # 1029 % 1024 = 5
    
    # Invalid
    with pytest.raises(ValueError, match="Full GPS Week"):
        validate_gps_week(1029, 6)
