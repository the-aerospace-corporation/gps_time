# gps_time

GPS Time representation and tools for Python.

## Breaking Change

Prior to version 3.x, `gps_time` did not include any timezone
information, i.e. all datetimes used by `gps_time` were “naive”. This
could lead to errors for versions of python that default to “aware”
datetime objects. In version 3, `gps_time` is updated to function using
aware datetime objects. If you pass `gps_time` a naive datetime, it will
assume that it is meant to represent UTC time. As this was the expected
behavior, there should be minimal impact, but this may result in errors
to existing code bases.

## Install

Installation can be achieved using `pip`, specifically

``` sh
pip install gps_time
```

## How to use

This module is relatively straightfoward to use. The
[`GPSTime`](api/core.md)
objects are generated (using arbitrary numbers) by

``` python
from gps_time import GPSTime
gps_time1 = GPSTime(week_number=1872, time_of_week=3324.654324324234324)
gps_time2 = GPSTime(week_number=1875, time_of_week=9890874.32)
```

    2

Notice that the time of week for `gps_time2` is longer than a week. The
[`GPSTime`](api/core.md)
object will automatically adjust the week number and time of week to
reasonable values.

``` python
print(gps_time2)
```

### Conversion

The
[`GPSTime`](api/core.md)
objects can also created from `datetime.datetime` objects

``` python
import datetime
gps_time3 = GPSTime.from_datetime(datetime.datetime(2017, 9, 2, 13, 23, 12, 211423))
print(gps_time3)
```

[`GPSTime`](api/core.md)
can likewise be converted to `datetime.datetime` object. However, one
must be careful because `datetime.datetime` objects only preserve
microsecond resolution. Converting from
[`GPSTime`](api/core.md)
to `datetime.datetime` can lose information. The opposite conversion
does not lose information.

``` python
print(f"GPS Time: {gps_time1}")
print(f"Datetime: {gps_time1.to_datetime()}")
print("")
print(f"Lost Precision: {gps_time1 - GPSTime.from_datetime(gps_time1.to_datetime())}")
```

### Operators

[`GPSTime`](api/core.md)
has comparison operators defined (equality, less than, etc.). It also
has addition and subtraction defined. In general, one can add/subtract
either `float`s or other
[`GPSTime`](api/core.md)s.

For floats, it is interpreted as a time shift in seconds (forward for
addition, backward for subtraction). This operation accounts for the
time of week. In-place addition and subtraction, i.e. the `+=` and `-=`
operators are supported for floats.

``` python
time_shift_seconds = 23431123.3243

print(f"Addition (float):    {gps_time2 + time_shift_seconds}")
print(f"Subtraction (float): {gps_time2 - time_shift_seconds}")
```

Alternatively, addition and subtraction can be done using two
[`GPSTime`](api/core.md)
objects. Subtraction finds the time difference in seconds (as a float).
Addition essentially sums the week numbers and times of week. Notice
that in-place addition and subtraction are not supported for two
[`GPSTime`](api/core.md)
objects.

``` python
print(f"Addition (GPSTime):    {gps_time2 + gps_time1}")
print(f"Subtraction (GPSTime): {gps_time2 - gps_time1}")
```

## License

Copyright (2020) The Aerospace Corporation. All Rights Reserved

The `gps_time` module releasded under the Apache2 license.
