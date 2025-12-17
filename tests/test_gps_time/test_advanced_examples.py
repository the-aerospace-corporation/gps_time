
import pytest
import datetime
from gps_time.core import GPSTime
from gps_time.leapseconds import utc2gps

def test_advanced_precision_example():
    """Verify sub-microsecond precision example."""
    # Example code from docs:
    delta_seconds = 1e-9 # 1 nanosecond

    # START: GPSTime
    dt = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    gps_t = GPSTime.from_datetime(dt)
    gps_t = gps_t + delta_seconds

    # Verification
    # 1ns = 1,000,000 femtoseconds
    assert gps_t.femtoseconds == 1_000_000
    
    # Verify standard datetime would fail this specific check if we tried to add it directly
    # Note: datetime doesn't support nanoseconds, so converting back might lose it depending on implementation,
    # but here we verify GPSTime KEPT it.

def test_advanced_leap_second_interval_example():
    """Verify leap second physical interval example."""
    # Example code from docs:
    t1_utc = datetime.datetime(2016, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
    t2_utc = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

    # --- Standard Datetime subtraction ---
    diff_utc = (t2_utc - t1_utc).total_seconds()
    # Verification: standard datetime thinks this is 1 second
    assert diff_utc == 1.0 

    # --- GPSTime subtraction ---
    t1_gps = utc2gps(t1_utc)
    t2_gps = utc2gps(t2_utc)

    diff_gps = t2_gps - t1_gps
    
    # Verification: GPSTime knows it is 2 seconds (1 sec normal + 1 leap sec)
    # Note: t1_gps is before the leap second (LS=17). 
    # t2_gps is after the leap second (LS=18).
    # Wait, let's trace:
    # t1_utc -> gps. LS at this time is 17. GPS = UTC + 17.
    # t2_utc -> gps. LS at this time is 18. GPS = UTC + 18.
    
    # t2_utc (in seconds) - t1_utc (in seconds) = 1.
    # t2_gps = (UTC_seconds + 1) + 18
    # t1_gps = UTC_seconds + 17
    # diff = (UTC + 1 + 18) - (UTC + 17) = UTC + 19 - UTC - 17 = 2.
    assert diff_gps == 2.0

def test_yaml_serialization(tmp_path):
    """Verify YAML serialization example."""
    from ruamel.yaml import YAML
    from gps_time.core import GPSTime

    # Initialize YAML object
    yaml = YAML()
    yaml.register_class(GPSTime)

    # Create a GPSTime object
    original_time = GPSTime(week_number=2139, seconds=12345.678)
    
    # Save to a temporary file
    test_file = tmp_path / "time.yaml"
    with open(test_file, 'w') as f:
        yaml.dump(original_time, f)
        
    # Load from the file
    with open(test_file, 'r') as f:
        loaded_time = yaml.load(f)
        
    # Verification
    assert isinstance(loaded_time, GPSTime)
    assert loaded_time == original_time
    assert loaded_time.week_number == 2139
    assert loaded_time.time_of_week == 12345.678
