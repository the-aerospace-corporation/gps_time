# Advanced Examples

This page demonstrates scenarios where `GPSTime` provides critical advantages over standard Python `datetime` objects, specifically regarding precision and physical time intervals.

## 1. Sub-Microsecond Precision

Standard `datetime` objects are limited to microsecond ($10^{-6}$) precision. `GPSTime` supports femtosecond ($10^{-15}$) precision.

### The Problem with Datetime
When performing calculations with extremely small time steps (e.g., in high-frequency signal processing or orbital mechanics), standard datetimes will truncate data.

```python
import datetime
from gps_time.core import GPSTime

# A very small time increment (1 nanosecond = 1e-9 seconds)
delta_seconds = 1e-9

# START: Datetime
dt = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
# Datetime only supports microseconds. 1ns is too small to be registered if added as a float directly
# or will be lost if converting to/from standard representations that don't support it.
# Note: datetime arithmetic generally requires timedeltas, resolution is limited.

# START: GPSTime
gps_t = GPSTime.from_datetime(dt)
gps_t = gps_t + delta_seconds

# GPSTime preserves the femtoseconds
# Expected: The time of week should reflect the addition
# 1ns = 1,000,000 femtoseconds
print(f"Added 1ns. Femtoseconds: {gps_t.femtoseconds}") 
```

## 2. True Physical Intervals (Leap Seconds)

Calculating the duration between two timestamps can be misleading when using UTC because UTC includes discontinuities (leap seconds). `GPSTime` is a continuous time scale, making it ideal for measuring true physical duration.

### Scenario: The 2016 Leap Second
A positive leap second was inserted at the end of December 31, 2016.
- **T1**: 2016-12-31 23:59:59 UTC
- **T2**: 2017-01-01 00:00:00 UTC

In real physical time, 2 seconds elapsed between these two markers (23:59:59 -> 23:59:60 -> 00:00:00).
However, standard `datetime` math (which is ignorant of leap seconds) will say only 1 second elapsed.

```python
import datetime
from gps_time.core import GPSTime
from gps_time.leapseconds import utc2gps

# Define the times surrounding the leap second
t1_utc = datetime.datetime(2016, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
t2_utc = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

# --- Standard Datetime subtraction ---
diff_utc = (t2_utc - t1_utc).total_seconds()
print(f"Datetime computed difference: {diff_utc} seconds") 
# Output: 1.0 (INCORRECT for physical elapsed time)

# --- GPSTime subtraction ---
# Convert to GPS Time (which accounts for the leap second insertion)
t1_gps = utc2gps(t1_utc)
t2_gps = utc2gps(t2_utc)

diff_gps = t2_gps - t1_gps
print(f"GPSTime computed difference: {diff_gps} seconds")
# Output: 2.0 (CORRECT physical elapsed time)
```

## 3. Serialization with Ruamel.YAML

`GPSTime` objects can be easily serialized to and from YAML using the `ruamel.yaml` library. This is useful for saving configuration or state that includes precise timestamps.

```python
import sys
from ruamel.yaml import YAML
from gps_time.core import GPSTime

# Initialize YAML object
yaml = YAML()
# Register the GPSTime class so YAML knows how to represent it
yaml.register_class(GPSTime)

# Create a GPSTime object
original_time = GPSTime(week_number=2139, seconds=12345.678)

# Serialize to YAML (printed to stdout here, but can be a file)
print("--- YAML Output ---")
yaml.dump(original_time, sys.stdout)

# To save to a file:
# with open('time.yaml', 'w') as f:
#     yaml.dump(original_time, f)

# To load from a file:
# with open('time.yaml', 'r') as f:
#     loaded_time = yaml.load(f)
```

