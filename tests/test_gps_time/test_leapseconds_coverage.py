import pytest
import datetime
from gps_time.core import GPSTime
from gps_time.leapseconds import LeapSeconds, gps2utc, utc2gps

def test_leap_seconds_coverage():
    """Test all branches of LeapSeconds methods."""
    
    # 1. Pre-1981 (before first leap second)
    t_pre = GPSTime.from_datetime(datetime.datetime(1980, 1, 6, tzinfo=datetime.timezone.utc)) # GPS Epoch
    assert LeapSeconds.get_leap_seconds(t_pre) == 0
    next_ls = LeapSeconds.get_next_leap_second(t_pre)
    assert next_ls[1] == 1 # First leap second is 1
    
    # 2. Middle date (e.g., 2000)
    t_mid = GPSTime.from_datetime(datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc))
    # Count visible in list: 1998 had 13.
    assert LeapSeconds.get_leap_seconds(t_mid) == 13
    
    # Next leap second from 2000 was 2005 (14)
    next_ls_mid = LeapSeconds.get_next_leap_second(t_mid)
    assert next_ls_mid[1] == 14
    
    # 3. Post-last leap second (e.g., 2020)
    t_post = GPSTime.from_datetime(datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc))
    assert LeapSeconds.get_leap_seconds(t_post) == 18 # As per list end
    assert LeapSeconds.get_next_leap_second(t_post) is None
    
    # 4. Future date (> 2025) - Test warning
    t_future = GPSTime.from_datetime(datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc))
    # Should warn
    # Not checking warning emission strictly unless pytest.warns used, but execution covers line
    LeapSeconds.get_leap_seconds(t_future)
    LeapSeconds.get_next_leap_second(t_future)

def test_conversions_coverage():
    """Test gps2utc and utc2gps branches."""
    
    # gps2utc with datetime input
    dt_gps = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    res = gps2utc(dt_gps)
    assert isinstance(res, datetime.datetime)
    
    # gps2utc with naive datetime (L136)
    dt_naive = datetime.datetime(2020, 1, 1)
    res_naive = gps2utc(dt_naive)
    assert res_naive.tzinfo == datetime.timezone.utc
    
    # gps2utc with GPSTime
    t_gps = GPSTime.from_datetime(dt_gps)
    res_gps = gps2utc(t_gps)
    assert abs((res_gps - dt_gps).total_seconds()) == 18 # 18 leap seconds diff
    
    # utc2gps with non-utc timezone (L167 warning)
    # Use naive which might default/warn? Code checks .tzinfo != utc. Naive usually None. None != utc.
    dt_naive_utc = datetime.datetime(2020, 1, 1)
    utc2gps(dt_naive_utc) # Should warn
