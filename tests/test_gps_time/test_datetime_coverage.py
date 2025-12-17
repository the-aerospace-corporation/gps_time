import pytest
import datetime
import numpy as np
from gps_time.datetime import (
    cast_to_datetime,
    datetime2tow,
    array_time_difference,
    correct_week,
    tow2datetime,
    tow2zcount,
    zcount2tow,
    zcount2datetime,
    datetime2zcount,
)

def test_cast_to_datetime_error():
    """Test error handling in cast_to_datetime (L59)."""
    with pytest.raises(IOError, match="not in ISO Time Format"):
        cast_to_datetime("invalid-date-string")

def test_datetime2tow_coverage():
    """Test branches in datetime2tow (L350, L353)."""
    # Test TypeError (L350)
    with pytest.raises(TypeError, match="must be a datetime object"):
        datetime2tow("not-a-datetime")
        
    # Test tzinfo is None handling (L353)
    dt_naive = datetime.datetime(2020, 1, 1)
    week, tow = datetime2tow(dt_naive)
    assert week > 0
    assert tow >= 0

def test_array_time_difference_errors():
    """Test error handling in array_time_difference."""
    dt = datetime.datetime(2020, 1, 1)
    
    # Test single datetime conversion (L123-126) -> Implicitly tested if we pass single dt.
    # Logic actually handles single instance but returns array.
    
    # Test TypeError: not arrays (L132)
    with pytest.raises(TypeError, match=r"must be\s+NumPy arrays"):
        array_time_difference("a", "b")
        
    # Test TypeError: array of non-datetimes checking (L139, L141)
    arr_dt = np.array([dt])
    arr_bad = np.array([1, 2, 3])
    
    with pytest.raises(TypeError, match="DateTimeArray1 must be an array"):
        array_time_difference(arr_bad, arr_dt)
        
    with pytest.raises(TypeError, match="DateTimeArray2 must be an array"):
        array_time_difference(arr_dt, arr_bad)

def test_correct_week_errors():
    """Test errors in correct_week (L181, L206)."""
    # Test non-int year (L181)
    with pytest.raises(ValueError, match="year must be an int"):
        correct_week(0, 0, 2020.5)

    # Test inconsistent week/year (L206) - Loop exhausted
    # Week 0 is 1980. Asking for year 1979 should fail or asking for 1980 but week is too far?
    # If we ask for year 2020 but provide week 0 (1980), it adds 1024 weeks until it hits 2020.
    # It fails if it skips over the year.
    # Week 0 -> 1980. +1024w -> 1999. +1024w -> 2019. +1024w -> 2038.
    # So if we ask for year 2000, it will check 1980 (<=2000), 1999 (<=2000), 2019 (>2000 loop ends).
    # Then checks if current_year.year (2019) == 2000? No.
    # Wait, loop condition is `while current_year.year <= year`.
    # Iter 1: 1980 <= 2000. Match? No. Add 1024 -> 1999.
    # Iter 2: 1999 <= 2000. Match? No. Add 1024 -> 2019.
    # Iter 3: 2019 <= 2000? False. Loop ends.
    # Else block runs? No, `else` on while loop runs if loop completes normally (condition false).
    # So it runs. Raises ValueError.
    with pytest.raises(ValueError, match="inconsistent"):
        correct_week(0, 0, 2000)

def test_wrappers_with_year():
    """Test year correction arguments in wrappers (L427, L470, L506)."""
    # Week 0 (Jan 1980). If we say year 1999, it should adjust to week 1024.
    week, tow = 0, 0.0
    
    # tow2datetime with year
    dt = tow2datetime(week, tow, year=1999)
    assert dt.year == 1999
    
    # tow2zcount with year
    w, z = tow2zcount(week, tow, year=1999)
    assert w == 1024
    
    # zcount2tow with year
    w2, t2 = zcount2tow(week, 0.0, year=1999)
    assert w2 == 1024
    
    # zcount2datetime coverage
    dt2 = zcount2datetime(week, 0.0, year=1999)
    assert dt2.year == 1999
    
    # datetime2zcount coverage
    # Just needs to run
    datetime2zcount(dt)

def test_cast_to_datetime_variations():
    """Test cast_to_datetime missing branches (L55)."""
    # ISO string without microseconds
    dt = cast_to_datetime("2020-01-01T12:00:00")
    assert dt.microsecond == 0

def test_unused_functions_coverage():
    """Test simple one-liners that weren't hit."""
    dt = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    
    # datetime_to_iso (L88)
    # imported as datetime_to_iso
    from gps_time.datetime import datetime_to_iso, diff_seconds, subtract_timedelta, subtract_timedelta_as_tow
    iso = datetime_to_iso(dt)
    assert "T" in datetime_to_iso(dt)

    # array_time_difference success path (L123, L145)
    delta = array_time_difference(dt, dt)
    assert len(delta) == 1
    assert delta[0] == 0

    # diff_seconds (L290)
    res = diff_seconds(dt, [dt])
    assert res[0] == 0
    
    # subtract_timedelta (L317)
    arr = np.array([dt])
    deltas = np.array([1.0])
    res2 = subtract_timedelta(arr, deltas)
    assert res2[0] == dt - datetime.timedelta(seconds=1)
    
    # subtract_timedelta_as_tow (L392)
    res3 = subtract_timedelta_as_tow(arr, deltas)
    assert len(res3) == 1

