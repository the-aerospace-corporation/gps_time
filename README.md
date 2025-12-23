# gps_time

![CI](https://github.com/the-aerospace-corporation/gps_time/actions/workflows/test.yaml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/gps_time)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gps_time)
![PyPI - License](https://img.shields.io/pypi/l/gps_time)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Coverage](https://raw.githubusercontent.com/the-aerospace-corporation/gps_time/master/coverage.svg)

[Documentation](https://the-aerospace-corporation.github.io/gps_time/) | [GitHub](https://github.com/the-aerospace-corporation/gps_time) | [PyPI](https://pypi.org/project/gps_time/)


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
[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)
objects are generated (using arbitrary numbers) by

``` python
gps_time1 = GPSTime(week_number=1872, time_of_week=3324.654324324234324)
gps_time2 = GPSTime(week_number=1875, time_of_week=9890874.32)
```

    2

Notice that the time of week for `gps_time2` is longer than a week. The
[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)
object will automatically adjust the week number and time of week to
reasonable values.

``` python
print(gps_time2)
```

### Conversion

The
[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)
objects can also created from `datetime.datetime` objects

gps_time3 = GPSTime.from_datetime(datetime.datetime(2017, 9, 2, 13, 23,
12, 211423)) print(gps_time3)

[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)
can likewise be converted to `datetime.datetime` object. However, one
must be careful because `datetime.datetime` objects only preserve
microsecond resolution. Converting from
[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)
to `datetime.datetime` can lose information. The opposite conversion
does not lose information.

``` python
print(f"GPS Time: {gps_time1}")
print(f"Datetime: {gps_time1.to_datetime()}")
print("")
print(f"Lost Precision: {gps_time1 - GPSTime.from_datetime(gps_time1.to_datetime())}")
```

### Operators

[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)
has comparison operators defined (equality, less than, etc.). It also
has addition and subtraction defined. In general, one can add/subtract
either `float`s or other
[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)s.

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
[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)
objects. Subtraction finds the time difference in seconds (as a float).
Addition essentially sums the week numbers and times of week. Notice
that in-place addition and subtraction are not supported for two
[`GPSTime`](https://the-aerospace-corporation.github.io/gps_time/core.html#gpstime)
objects.

``` python
print(f"Addition (GPSTime):    {gps_time2 + gps_time1}")
print(f"Subtraction (GPSTime): {gps_time2 - gps_time1}")
```

## License

Copyright (2020) The Aerospace Corporation. All Rights Reserved

The `gps_time` module releasded under the Apache2 license.

### Open Source Licenses

This module is built on the `nbdev` template, which is used under the
Apache2 license.

## Formatting

As much as possible for jupyter notebooks, the
[black](https://black.readthedocs.io/en/stable/) formatting standard
will be used. To apply black to jupyter notebooks, the
[jupyter-black](https://github.com/drillan/jupyter-black) extension can
be used.
