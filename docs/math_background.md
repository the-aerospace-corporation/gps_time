# Math and Background

This document explains the mathematical concepts and data representations used in the `gps_time` library.

## Time Scales

### GPS Time vs. UTC

Global Positioning System (GPS) Time is a continuous time scale that does not include leap seconds. It started on **January 6, 1980**.

Coordinated Universal Time (UTC), however, includes leap seconds to keep the time scale synchronized with the Earth's rotation.

The relationship between GPS Time and UTC is:

$$ GPS = UTC + LS $$

Where $LS$ is the number of leap seconds introduced since Jan 6, 1980.

### Code Example: Converting GPS to UTC

```python
import datetime
from gps_time.core import GPSTime
from gps_time.leapseconds import gps2utc

# GPS Time: Week 2139, 1000.0 seconds
gps_t = GPSTime(week_number=2139, seconds=1000)
utc_t = gps2utc(gps_t)

print(f"GPS Time: {gps_t}")
print(f"UTC Time: {utc_t}")
```

## Data Representation

### Weeks and Time of Week (TOW)

GPS Time is commonly represented as a "Week Number" and "Seconds of Week" (Time of Week or TOW).

- **Week Number**: Counts the number of weeks since the epoch (Jan 6, 1980). Note that the broadcast GPS signal uses a 10-bit week number (rolling over every 1024 weeks), but this library typically uses the full (extended) week number.
- **TOW**: Seconds since midnight Saturday/Sunday. Range: $0 \le TOW < 604800$.

### Code Example: Week Rollover

The `GPSTime` class automatically handles handling seconds that exceed the week duration by incrementing the week number.

```python
from gps_time.core import GPSTime

# 604800 seconds is exactly one week
t = GPSTime(week_number=1000, seconds=604805)

# Should normalize to Week 1001, 5 seconds
print(f"Week: {t.week_number}, Seconds: {t.seconds}") 
```

### Femtosecond Precision

Standard floating-point numbers (doubles) do not have enough precision to represent nanosecond-level timing when measuring time from an epoch years in the past. To solve this, `GPSTime` stores:

1.  **Week Number** (int)
2.  **Seconds** (int)
3.  **Femtoseconds** (int) - $10^{-15}$ seconds.

This allows for extremely high precision without floating-point errors.

## Z-Count

The Z-Count is a truncated time representation often used in GPS navigation messages. It represents time in 1.5-second epochs.

$$ ZCount = \frac{TOW}{1.5} $$

Consequently, one Z-Count unit equals 1.5 seconds.

### Code Example: Z-Count Conversion

```python
from gps_time.core import GPSTime

t = GPSTime(week_number=2000, seconds=150)
z = t.to_zcount()

print(f"TOW: {t.time_of_week}")
print(f"Z-Count: {z}") # Should be 100.0
```
