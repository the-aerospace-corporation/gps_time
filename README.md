# gps_time
> Tools for handling time related to GPS


This module is used to represent GPS time and provide tools for handling it. The tools developed here were originally made in pure python, but were later converted to jupyter notebooks using `nbdev`. The goal is to provide an absolute time representation for python that is easer to use for scientific computing and with higher resolution than the built-in `datetime`.

## Install

Installation can be achieved using `pip`, specifically
```bash
pip install gps-time
```

## How to use

This module is relatively straightfoward to use. The `GPSTime` objects are generated (using arbitrary numbers) by

```
gps_time1 = GPSTime(week_number=1872, time_of_week=3324.654324324234324)
gps_time2 = GPSTime(week_number=1875, time_of_week=9890874.32)
```

Notice that the time of week for `gps_time2` is longer than a week. The `GPSTime` object will automatically adjust the week number and time of week to reasonable values.

```
gps_time2
```




    GPSTime(week_number=1891, time_of_week=214074.3200000003)



### Conversion

The `GPSTime` objects can also created from `datetime.datetime` objects

```
gps_time3 = GPSTime.from_datetime(datetime.datetime(2017, 9, 2, 13, 23, 12, 211423))
print(gps_time3)
```

    GPSTime(week_number=1964, time_of_week=566592.211423)


`GPSTime` can likewise be converted to `datetime.datetime` object. However, one must be careful because `datetime.datetime` objects only preserve microsecond resolution. Converting from `GPSTime` to `datetime.datetime` can lose information. The opposite conversion does not lose information.

```
print(f"GPS Time: {gps_time1}")
print(f"Datetime: {gps_time1.to_datetime()}")
print("")
print(f"Lost Precision: {gps_time1 - GPSTime.from_datetime(gps_time1.to_datetime())}")
```

    GPS Time: GPSTime(week_number=1872, time_of_week=3324.6543243242345)
    Datetime: 2015-11-22 00:55:24.654324
    
    Lost Precision: 3.2423440643469803e-07


### Operators
`GPSTime` has comparison operators defined (equality, less than, etc.). It also has addition and subtraction defined. In general, one can add/subtract either `float`s or other `GPSTime`s.

For floats, it is interpreted as a time shift in seconds (forward for addition, backward for subtraction). This operation accounts for the time of week. In-place addition and subtraction, i.e. the `+=` and `-=` operators are supported for floats.

```
time_shift_seconds = 23431123.3243

print(f"Addition (float):    {gps_time2 + time_shift_seconds}")
print(f"Subtraction (float): {gps_time2 - time_shift_seconds}")
```

    Addition (float):    GPSTime(week_number=1930, time_of_week=57997.64429999888)
    Subtraction (float): GPSTime(week_number=1852, time_of_week=370150.9957000017)


Alternatively, addition and subtraction can be done using two `GPSTime` objects. Subtraction finds the time difference in seconds (as a float). Addition essentially sums the week numbers and times of week. Notice that in-place addition and subtraction are not supported for two `GPSTime` objects.

```
print(f"Addition (GPSTime):    {gps_time2 + gps_time1}")
print(f"Subtraction (GPSTime): {gps_time2 - gps_time1}")
```

    Addition (GPSTime):    GPSTime(week_number=3763, time_of_week=217398.97432432455)
    Subtraction (GPSTime): 11701949.665675675


## License

Copyright (2020) The Aerospace Corporation. All Rights Reserved

The `gps_time` module releasded under the Apache2 license.

### Open Source Licenses
This module is built on the `nbdev` template, which is used under the Apache2 license.


## Formatting

As much as possible for jupyter notebooks, the [black](https://black.readthedocs.io/en/stable/) formatting standard will be used. To apply black to jupyter notebooks, the [jupyter-black](https://github.com/drillan/jupyter-black) extension can be used.
