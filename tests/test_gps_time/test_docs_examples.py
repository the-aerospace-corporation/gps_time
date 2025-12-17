
import pytest
import datetime
from gps_time.core import GPSTime
from gps_time.leapseconds import gps2utc

def test_example_gps_to_utc():
    """Verify the 'Converting GPS to UTC' example."""
    # Example code from docs:
    # GPS Time: Week 2139, 1000.0 seconds
    gps_t = GPSTime(week_number=2139, seconds=1000)
    utc_t = gps2utc(gps_t)

    # Verification
    # Week 2139 is in Jan 2021.
    # 2139 weeks * 7 days + 1000 seconds
    # Epoch: Jan 6, 1980
    
    # Expected UTC time calculation (manual or trusted source verification)
    # gps-time (no leap seconds) -> utc-time (with leap seconds)
    # 2139 weeks is roughly 41 years. 
    # Let's rely on the library being internally consistent for a "smoke test" 
    # but check against a concrete known value if possible.
    # We know from test_leapseconds that 2021 has 18 leap seconds (since 2017).
    # So UTC should be GPS - 18 seconds.
    
    # 2139 weeks from 1980-01-06 is 2021-01-03.
    # + 1000 seconds.
    # 2021-01-03 00:00:00 UTC = GPS 2139 0.
    # GPS 2139 1000 = 2021-01-03 00:16:40 GPS time.
    # UTC = GPS - 18s = 2021-01-03 00:16:22 UTC.
    
    expected_utc = datetime.datetime(2021, 1, 3, 0, 16, 22, tzinfo=datetime.timezone.utc)
    assert utc_t == expected_utc

def test_example_week_rollover():
    """Verify the 'Week Rollover' example."""
    # Example code from docs:
    t = GPSTime(week_number=1000, seconds=604805)
    
    # Verification
    assert t.week_number == 1001
    assert t.seconds == 5

def test_example_z_count():
    """Verify the 'Z-Count Conversion' example."""
    # Example code from docs:
    t = GPSTime(week_number=2000, seconds=150)
    z = t.to_zcount()

    # Verification
    assert t.time_of_week == 150.0
    assert z == 100.0
