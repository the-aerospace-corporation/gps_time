import pytest
import ruamel.yaml
from gps_time.core import GPSTime
from io import StringIO

def test_gpstime_constructor_errors():
    """Test exceptions and warnings in GPSTime constructor."""
    # Test mixed positional and keyword arguments (L127)
    with pytest.raises(ValueError, match="positional and keyword arguments"):
        GPSTime(100, 200, seconds=300)

    # Test warning when no arguments given (L151-155)
    # Note: week_number is always required first arg, so "no arguments" means no time args
    gpstime = GPSTime(100)
    assert gpstime.week_number == 100
    assert gpstime.seconds == 0
    assert gpstime.femtoseconds == 0

    # Test compatibility: femtoseconds without seconds (L174)
    with pytest.raises(ValueError, match=r"must be\s+accompanied by"):
        GPSTime(100, femtoseconds=500)

    # Test invalid keyword arguments (L187)
    with pytest.raises(ValueError, match="Invalid Keyword arguments"):
        GPSTime(100, invalid_arg=123)
        
    # Test incompatible kwargs (L159)
    with pytest.raises(ValueError, match=r"are incompatible"):
        GPSTime(100, time_of_week=100.0, femtoseconds=50)

    # Test too many kwargs (L149)
    with pytest.raises(ValueError, match="Too many arguments"):
        GPSTime(100, a=1, b=2, c=3)

    # Test warning when float used in seconds/femtoseconds (L164-170)
    GPSTime(100, seconds=100.5, femtoseconds=0)

    # Test warning when float used in positional seconds/femto (L138-142)
    GPSTime(100, 100.5, 0)
    
    # Test valid handling of seconds-only keyword (L178-183)
    t = GPSTime(100, seconds=123.456)
    assert t.time_of_week == 123.456

def test_from_yaml_errors(): 
    """Test error conditions in from_yaml."""
    yaml = ruamel.yaml.YAML()
    yaml.register_class(GPSTime)

    # Error: no seconds/time_of_week (L253)
    yaml_str = """
    !GPSTime
    week_number: 2000
    """
    with pytest.raises(ValueError, match="lacked both"):
        yaml.load(StringIO(yaml_str))

    # Error: both seconds and time_of_week (L255)
    yaml_str = """
    !GPSTime
    week_number: 2000
    seconds: 100
    time_of_week: 100.0
    """
    with pytest.raises(ValueError, match="defines both time_of_week and seconds"):
        yaml.load(StringIO(yaml_str))

    # Error: time_of_week and femtoseconds (L259)
    yaml_str = """
    !GPSTime
    week_number: 2000
    time_of_week: 100.0
    femtoseconds: 50
    """
    with pytest.raises(ValueError, match="defines both time_of_week and femtoseconds"):
        yaml.load(StringIO(yaml_str))
        
    # Legacy path: seconds but no femtoseconds (L263)
    # Pass seconds as string to force it into construct_scalar logic if needed? 
    # Logic: seconds is not None, femtoseconds is None
    yaml_str = """
    !GPSTime
    week_number: 2000
    seconds: 100.5
    """
    t = yaml.load(StringIO(yaml_str))
    assert t.week_number == 2000
    # 100.5 seconds -> 100s, 5e14 fs
    assert t.seconds == 100
    assert t.femtoseconds == 500000000000000

def test_correct_weeks_deprecated():
    """Test the deprecated correct_weeks method (L347-357)."""
    t = GPSTime(100, 0)
    t.seconds = 604800 + 100 # Manually set to overflow
    t.correct_weeks() # Should trigger warning and logic
    assert t.week_number == 101
    assert t.time_of_week == 100.0

def test_correct_weeks_valid_deprecated():
    """Test deprecation correct_weeks with valid time (L356 else)."""
    t = GPSTime(100, 100)
    t.correct_weeks() # Should do nothing
    assert t.week_number == 100
    assert t.time_of_week == 100.0
