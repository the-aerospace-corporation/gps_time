
__all__ = ['ISO_FMT', 'cast_to_datetime', 'datetime_to_iso', 'array_time_difference', 'correct_week', 'arange_datetime',
           'diff_seconds', 'subtract_timedelta', 'datetime2tow', 'subtract_timedelta_as_tow', 'tow2datetime',
           'tow2zcount', 'zcount2tow', 'datetime2zcount', 'zcount2datetime']


"""Copyright 2020 The Aerospace Corporation"""


import re, datetime
import numpy as np

from typing import Iterable, List, Tuple, Optional


_gps_epoch_datetime: datetime.datetime = datetime.datetime(year=1980, month=1, day=6, tzinfo=datetime.timezone.utc)


ISO_FMT = r"([0-9]{4})-?([0-9]{2})-?([0-9]{2})[T| ]?([0-9]{2}):?([0-9]{2}):?([0-9]{2})\.?([0-9]{6})?"  # noqa: E501


def cast_to_datetime(iso_string: str) -> datetime.datetime:
    """Cast an ISO string to a datetime object.

    Iso format is defined as YYYY-MM-DDTHH:MM:SS.SSSSSS, for this cast the
    formatters (- : . T) are all optional, technically all thats needed is
    a 20 digit integer with the values in the right place

    Parameters
    ----------
    iso_string : str
        string to convert to datetime

    Returns
    -------
    datetime.datetime
        The datetime defined by the string

    See Also
    --------
    `ISO_FMT`

    """

    """    
    Raises
    ------
    IOError
        If the input does not contain an ISO datetime format
    """

    m = re.match(ISO_FMT, iso_string)
    if m is not None:
        y, m, d, h, minute, s, us = [int(v) if v is not None else v for v in m.groups()]
        if us is None:
            us = 0
        return datetime.datetime(year=y, month=m, day=d, hour=h, minute=minute, second=s, microsecond=us, tzinfo=datetime.timezone.utc)

    else:
        raise IOError("Value {} not in ISO Time Format".format(iso_string))


def datetime_to_iso(date_time: datetime.datetime) -> str:
    """Convert a datetime to an iso string.

    The purpose of this function is to convert a datetime object to a string
    in the standard ISO format.

    Parameters
    ----------
    date_time : datetime.datetime
        A datetime object

    Returns
    -------
    str
        A string containing the ISO formatted time, i.e.
        YYYY-MM-DDTHH:MM:SS.SSSSSS

    Todo
    ----
    .. todo:: Determine Usefulness
        This appears to alias the datetime built-in isoformat() function.
        Determine if this function should still be included or it provides
        additional functionality

    """
    return "T".join(str(date_time).split(" "))


def array_time_difference(
    datetime_array1: np.ndarray, datetime_array2: np.ndarray
) -> np.ndarray:
    r"""Get time delta (sec) from arrays of datetime.

    The purpose of this function is to compute the time between two arrays of
    datetime objects. If the first argument is \(T_{1}\) and the second
    argument is \(T_{2}\), then this function returns
    \(T_{1} - T_{2}\) in seconds. If a single DateTime object is given for
    one of the arguments, it is converted to a single element numpy array.

    Parameters
    ----------
    datetime_array1 : np.ndarray
        The first date time array
    datetime_array2 : np.ndarray
        The second date time array

    Returns
    -------
    np.ndarray
        A NumPy array containing the time from the the second datetime
        array to the first

    """

    """
    Raises
    ------
    TypeError
        If the inputs are not arrays of datetimes
    """
    if isinstance(datetime_array1, datetime.datetime):
        datetime_array1 = np.array([datetime_array1])
    if isinstance(datetime_array2, datetime.datetime):
        datetime_array2 = np.array([datetime_array2])

    if not (
        isinstance(datetime_array1, np.ndarray)
        and isinstance(datetime_array2, np.ndarray)
    ):
        raise TypeError(
            """Both DateTimeArray1 and DateTimeArray2 must be
                        NumPy arrays. Use numpy.array() to convert a list to
                        an NumPy array."""
        )

    if not (all(isinstance(x, datetime.datetime) for x in datetime_array1)):
        raise TypeError("DateTimeArray1 must be an array of DateTime objects")
    if not (all(isinstance(x, datetime.datetime) for x in datetime_array2)):
        raise TypeError("DateTimeArray2 must be an array of DateTime objects")

    time_delta = datetime_array1 - datetime_array2

    return np.array([x.total_seconds() for x in time_delta])





def correct_week(week_num: int, tow: float, year: int) -> int:
    """Correct the week number for week rollovers.

    Provide the mod 1024 week number and update to the actual GPS week based
    on the year

    Parameters
    ----------
    week_num : int
        The mod 1024 week number
    tow : float
        The time of week
    year : int
        The year

    Returns
    -------
    int
        The full GPS week number

    """

    """
    Raises
    ------
    ValueError
        If the year is not an int
    ValueError
        If the week number and year are inconsistent
    """
    if not isinstance(year, int):
        raise ValueError("The year must be an int")

    # Get the year for the week number
    current_year = _gps_epoch_datetime + datetime.timedelta(
        days=7 * week_num, seconds=tow
    )

    # While the week number is before the desired year, keep adding 1024
    # weeks and compare. Note that if a match is found, the while loop
    # breaks. If it is not, the while loop exits to else, which raises and
    # error.
    while current_year.year <= year:

        # Break when the year and year expressed by the week number are the
        # same.
        if current_year.year == year:
            break

        # Add 1024 weeks to the week number and recompute the current year
        week_num += 1024
        current_year = _gps_epoch_datetime + datetime.timedelta(
            days=7 * week_num, seconds=tow
        )
    else:  # If the week number is not consistent with the year
        raise ValueError("WeekNum and Year are inconsistent.")

    return week_num


def arange_datetime(
    start_datetime: datetime.datetime, duration_s: float, step_ms: float
) -> List[datetime.datetime]:
    """Create a list of datetimes in sequence.

    The purpose of this function is to create a list that represents a
    sequence of datetimes of the specified duration with the specified step
    size.

    This function is an analogue of the `numpy.arange()` function, but
    operates on datetimes.

    Parameters
    ----------
    start_gpstime : datetime.datetime
        The datetime to start the sequence
    duration_s : float
        The duration of the sequence, in seconds
    step_ms : float
        The step size, in milliseconds

    Returns
    -------
    List[datetime.datetime]
        The sequence of datetime

    Notes
    -----
    Like `numpy.arange`, this does not include the final element. That is, if
    the start is at 0 with a duration of 5 and step of 1, the sequence would
    return [0, 1, 2, 3, 4]

    See Also
    --------
    `numpy.arange()`
    `arange_gpstime()`

    Todo
    ----
    .. todo:: Determine if this still works if a np.ndarray is returned
        instead of a list

    """
    times = []
    dt = datetime.timedelta(milliseconds=step_ms)
    duration = datetime.timedelta(seconds=duration_s)
    end_date = start_datetime + duration
    while True:
        date = start_datetime + len(times) * dt
        if date < end_date:
            times.append(date)
        else:
            break
    return times


def diff_seconds(
    dt_obj: datetime.datetime, dt_array: Iterable[datetime.datetime]
) -> np.ndarray:
    """Get the time diff in seconds between a single date time and an array.

    This function is uses to find the time difference between a single datetime
    and an array of datetimes. It returns the value of the single datetime
    minus the array of datetimes

    Parameters
    ----------
    dt_obj : datetime.datetime
        A single datetime object
    dt_array : Iterable[datetime.datetime]
        An array of datetime objects

    Returns
    -------
    np.ndarray
        An array of time differences between dt_obj and each element of
        dt_array

    """
    return np.array([(dt_obj - dt).total_seconds() for dt in dt_array])


def subtract_timedelta(
    datetime_array: np.ndarray, time_delta: np.ndarray
) -> np.ndarray:
    """Subtract a time delta from an array of datetimes.

    This function is used to subtract an array of time deltas in seconds from
    an array of datetimes.

    Parameters
    ----------
    datetime_array : np.ndarray
        An array of datetimes
    time_delta : np.ndarray
        An array of timedeltas, in seconds

    Returns
    -------
    np.ndarray
        An array of datetimes that are the input datetime array with the
        time delta subtracted from them

    .. todo:: Add checks for inputs

    """
    return datetime_array - np.array(
        [datetime.timedelta(seconds=s) for s in time_delta]
    )


def datetime2tow(date_time: datetime.datetime) -> Tuple[int, float]:
    """Convert date time to GPS Week and Time of Week.

    The purpose of this function is to convert a datetime object to the GPS
    week number and the time of week. This returns the full GPS week number.
    The user must separately compute the mod 1024 week if that is desired.

    Parameters
    ----------
    date_time : datetime.datetime
        A datetime object representing the desired times. If no tzinfo is 
        provided, assumed to be UTC

    Returns
    -------
    Tuple[int, float]
        Two elements: 1) The GPS Week Number and 2) the time of week
    """

    """
    Raises
    ------
    TypeError
        If the input is not a datetime
    """
    
    # Ensure the argument is a datetime object
    if not isinstance(date_time, datetime.datetime):
        raise TypeError("DateTime arg must be a datetime object.")

    if date_time.tzinfo is None:
        date_time=date_time.replace(tzinfo=datetime.timezone.utc)

    # Find the week number
    week_num = (date_time - _gps_epoch_datetime).days // 7

    # Determine the first day of the week and compute the time since the start
    # of the week, in seconds
    week_start = _gps_epoch_datetime + datetime.timedelta(days=week_num * 7)
    time_since_week_start = date_time - week_start
    time_of_week = time_since_week_start.total_seconds()

    # Returns the week number and the time of week
    return int(week_num), float(time_of_week)


def subtract_timedelta_as_tow(
    datetime_array: np.ndarray, time_delta: np.ndarray
) -> np.ndarray:
    """Subtract time delta from an array of datetimes and return as week/TOW.

    This function is used to subtract an array of time deltas in seconds from
    an array of datetimes. It does this by calling subtract_timedelta() to get
    an array of new datetimes then using datetime2tow() to cast the datetimes
    in terms of week numbers and times of week.

    Parameters
    ----------
    datetime_array : np.ndarray
        An array of datetimes
    time_delta : np.ndarray
        An array of timedeltas, in seconds

    Returns
    -------
    np.ndarray
        An array of week numbers and times of weeks that are the input
        datetime array with the time delta subtracted from them

    """
    d = subtract_timedelta(datetime_array, time_delta)
    return np.array([datetime2tow(_d) for _d in d])


def tow2datetime(
    week_num: int, tow: float, year: Optional[int] = None
) -> datetime.datetime:
    """Convert GPS Week and Time of Week to datetime.

    The purpose of this function is to convert a GPS Week number and a time of
    week into a DateTime object. The week number represents the number of weeks
    since 6 January 1980 and the time of week is the number of seconds since
    midnight Sunday night. Note that the GPS week is sometimes expressed as a
    mod 1024 week. If this is the case, the Year argument can be used to
    correct for mod 1024 weeks. If the week number is not consistent with the
    Year, then an error is raised.

    Parameters
    ----------
    week_num : int
        GPS Week Number (not limited to 1024)
    tow : float
        Time of Week (seconds since midnight Sunday Morning)
    year : Optional[int], optional
        If not None, used to correct the week_num from mod 1024 week to
        the actual week number (weeks since 6 Jan 1980), by default None

    Returns
    -------
    datetime.datetime
        object that represents the current time

    """
    # Correct the week number if a year is given
    if year is not None:
        week_num = correct_week(week_num, tow, year)

    date_time_out = (
        _gps_epoch_datetime
        + datetime.timedelta(days=week_num * 7)
        + datetime.timedelta(seconds=tow)
    )

    # Return a datetime object that stores the current week
    return date_time_out


def tow2zcount(
    week_num: int, tow: float, year: Optional[int] = None
) -> Tuple[int, float]:
    """Convert a week number and time of week into week and zcount.

    The Z-Count is the time of week in seconds divided by 1.5. This function is
    used to convert from a time of week and week number to z-count.

    Parameters
    ----------
    week_num : int
        The week number
    tow : float
        The time of week (seconds)
    year : Optional[int], optional
        If not None, adjusts the week number to account for week roll
        overs. Otherwise, is passed through, by default None

    Returns
    -------
    Tuple[int, float]
        The week number and z-count

    Notes
    -----
    This function returns floating point z-count. Use another method to
    cast as int if required

    """
    # If not None, correct the week number base on the year
    if year is not None:
        week_num = correct_week(week_num, tow, year)

    # Z-count is the week number divided by 1.5
    zcount = tow / 1.5

    return week_num, zcount


def zcount2tow(
    week_num: int, zcount: float, year: Optional[int] = None
) -> Tuple[int, float]:
    """Convert a week number and time of week into week and zcount.

    The Z-Count is the time of week divided by 1.5. This function is used to
    convert from a z-count and week number to time of week.

    Parameters
    ----------
    week_num : int
        The week number
    zcount : float
        The z-count (1.5 sec epochs)
    year : Optional[int], optional
        If not None, adjusts the week number to account for week roll
        overs. Otherwise, is passed through, by default None

    Returns
    -------
    Tuple[int, float]
        The week number and time of week

    """
    tow = zcount * 1.5

    # If not None, correct the week number base on the year
    if year is not None:
        week_num = correct_week(week_num, tow, year)

    return week_num, tow


def datetime2zcount(date_time: datetime.datetime) -> Tuple[int, float]:
    """Convert a datetime to z-count and week number.

    This function takes a datetime and returns a week number and z-count. It
    accomplishes this by first calling datetime2tow() and then tow2zcount().

    Parameters
    ----------
    date_time : datetime.datetime
        The datetime

    Returns
    -------
    Tuple[int, float]
        The week number and z-count

    """
    week_num, tow = datetime2tow(date_time)
    week_num, zcount = tow2zcount(week_num, tow)

    return week_num, zcount


def zcount2datetime(
    week_num: int, zcount: float, year: Optional[int] = None
) -> datetime.datetime:
    """Convert a week number and time of week into a datetime.

    The Z-Count is the time of week divided by 1.5. This function is used to
    convert from a z-count and week number to the equivalent datetime. It
    accomplished this by calling zcount2tow() and then tow2datetime().

    Parameters
    ----------
    week_num : int
        The week number
    zcount : float
        The z-count (1.5 sec epochs)
    year : Optional[int], optional
        If not None, adjusts the week number to account for week roll
        overs. Otherwise, is passed through, by default None

    Returns
    -------
    datetime.datetime
        The datetime representing the zcount

    """
    week_num, tow = zcount2tow(week_num, zcount, year=year)
    date_time = tow2datetime(week_num, tow)

    return date_time
