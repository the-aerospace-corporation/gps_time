# AUTOGENERATED! DO NOT EDIT! File to edit: ../00_core.ipynb.

# %% ../00_core.ipynb 2
"""Copyright 2020 The Aerospace Corporation"""

# %% ../00_core.ipynb 4
from __future__ import annotations
import datetime
import ruamel.yaml

import numpy as np

from typing import Union, Tuple
from logging import getLogger

from .datetime import tow2datetime, datetime2tow

# %% auto 0
__all__ = ['logger', 'GPSTime']

# %% ../00_core.ipynb 5
logger = getLogger(__name__)

# %% ../00_core.ipynb 7
_SEC_IN_WEEK: int = 604800
_SEC_TO_FEMTO_SEC: float = 1.0e15
_FEMTO_SEC_TO_SEC: float = 1.0e-15

# %% ../00_core.ipynb 9
def _tow2sec(time_of_week: float) -> Tuple[int, int]:
    """Convert a float time to integer seconds and femtoseconds

    Parameters
    ----------
    time_of_week : float
        The time of week, as a float

    Returns
    -------
    Tuple[int, int]
        The seconds and femtoseconds within the time of week
    """
    seconds = int(time_of_week // 1)
    femtoseconds = int((time_of_week % 1) * _SEC_TO_FEMTO_SEC)
    return seconds, femtoseconds

# %% ../00_core.ipynb 11
class GPSTime:
    """Time representation for GPS.

    Parameters
    ----------
    week_number : int
        The number of weeks since the start of the GPS epoch, 6 Jan 1980.
    seconds : int
        The number of integer seconds into the week. The zero time is at
        midnight on Sunday morning, i.e. betwen Saturday and Sunday. Should
        be between 0 and 604800 because otherwise, the week number would be
        incorrect.
    femtoseconds : int
        The number of femtoseconds into the week. That is, this is the number
        of fractional seconds in the time of week with a scale factor of 1e15.
    """

    """
    Todo
    ----
    .. todo:: Create a GPSTimeDelta class to handle adding/subtracting with
        increase accuracy.

    """

    """
    Raises
    ------
    TypeError
        For various operators if not the selected types are not implemented.
    ValueError
        If an incorrect set of input arguments are provided to the constructor
    """

    weeks: int
    seconds: int
    femtoseconds: int

    yaml_tag: str = u"!GPSTime"

    def __init__(self, week_number: int, *args, **kwargs) -> None:
        """Object constructor.

        This sets the week number and the time of week and ensures that the
        time of week is a float. It also calls `correct_time()`, which checks
        to see if the time of week is negative or past the end of the week
        and adjust the values accordingly.

        This constructor supports many different input arguments. However some
        sets of input arguments may result in truncation and errors if a
        `float` is provided when an `int` is expected.

        Parameters
        ----------
        week_number : int
            The number of week
        *args, **kwargs
            The time of week in various representations. If positional arguments
            are used, a single positional argument is interpreted as a time of
            week (i.e. a float), while two arguments are interpreted as seconds
            and femtoseconds. In the latter case, the values will be cast as
            integers, which may result in truncation. Keyword arguments function
            in much the same way, with "time_of_week", "seconds", and
            "femtoseconds" being the valid keyword arguments. If only "seconds"
            is given, it will be treated like "time_of_week". If no additional
            arguments are given, the time is assumed to be the start of the week.
        """

        """
        Raises
        ------
        ValueError
            If invalid arguments are given. Examples include:
            - Mixed positional and keyword arguments are not supported
            - More than two arguments are not supported
            - Keyword arguments "time_of_week" and "femtoseconds" cannot be
              used together.

        """
        self.yaml_tag: str = u"!GPSTime"
        if len(args) > 0 and len(kwargs) > 0:
            raise ValueError(
                "GPSTime does not support both positional and keyword arguments."
            )

        self.week_number = int(week_number)
        if len(args) > 2:  # If more than 3 args (week + 2 times)
            raise ValueError(
                "Only up to three arguments allowed (Week number, seconds, "
                "and femtoseconds)"
            )
        elif len(args) == 2:
            if isinstance(args[0], float) or isinstance(args[1], float):
                logger.warning(
                    "Two times given, but at least one is a float. Decimal "
                    "values will be truncated"
                )
            self.seconds = int(args[0])
            self.femtoseconds = int(args[1])
        elif len(args) == 1:
            self.time_of_week = args[0]
        else:
            if len(kwargs) > 2:
                raise ValueError("Too many arguments")
            elif len(kwargs) == 0:
                logger.warning(
                    "No time of week information. Defaulting to start of week"
                )
                self.seconds = 0
                self.femtoseconds = 0

            elif "femtoseconds" in kwargs:
                if "time_of_week" in kwargs:
                    raise ValueError(
                        """Keyword arguments "time_of_week" and "femtoseconds"
                        are incompatible."""
                    )
                elif "seconds" in kwargs:
                    if isinstance(kwargs["seconds"], float) or isinstance(
                        kwargs["femtoseconds"], float
                    ):
                        logger.warning(
                            "Two times given, but at least one is a float. "
                            "Decimal values will be truncated"
                        )
                    self.seconds = int(kwargs["seconds"])
                    self.femtoseconds = int(kwargs["femtoseconds"])
                else:
                    raise ValueError(
                        """Keyword argument "femtoseconds" must be
                        accompanied by "seconds"."""
                    )
            elif "seconds" in kwargs:
                logger.warning(
                    "seconds given with no femtoseconds. Will be handled "
                    "as time of week"
                )
                self.time_of_week = float(kwargs["seconds"])
            elif "time_of_week" in kwargs:
                self.time_of_week = float(kwargs["time_of_week"])
            else:
                raise ValueError("Invalid Keyword arguments")

        self.correct_time()
        if self.week_number < 0:
            logger.warning("Week number is less than 0")

    @property
    def time_of_week(self) -> float:
        """The time of week as a float."""
        return float(self.seconds + self.femtoseconds * _FEMTO_SEC_TO_SEC)

    @time_of_week.setter
    def time_of_week(self, time_of_week: float) -> None:
        """A setter for the time of week.

        The method allows the seconds and femtoseconds to be updated using
        a single float.

        Paremeters
        ----------
        time_of_week : float
            The time of week as a float
        """
        sec, femtosec = _tow2sec(time_of_week)
        self.seconds = sec
        self.femtoseconds = femtosec

    @classmethod
    def from_yaml(
        cls: type, constructor: ruamel.yaml.Constructor, node: ruamel.yaml.MappingNode
    ) -> GPSTime:
        """YAML Constructor.

        This YAML constructor is used to load a GPSTime from a YAML file. It must be
        registered with the YAML loader. This is accomplished using
        ```python3
        import ruamel.yaml
        yaml = ruamel.yaml.YAML(typ="unsafe")
        yaml.register_class(GPSTime)
        ```

        This class method is primarily used to add a constructor to an instance of
        ruamel.yaml. Its functionality as a traditional classmethod is limited.

        .. note:: YAML Module
            This constructor is meant to be used with ruamel.yaml. It has not been tested
            with pyyaml (the more common YAML library.)

        """
        nodes = node.value
        week_number = None
        seconds = None
        femtoseconds = None
        time_of_week = None
        for i in range(0, len(nodes)):
            node_name = nodes[i][0].value
            if node_name == "week_number":
                week_number = constructor.construct_scalar(nodes[i][1])
            elif node_name == "seconds":
                seconds = constructor.construct_scalar(nodes[i][1])
            elif node_name == "femtoseconds":
                femtoseconds = constructor.construct_scalar(nodes[i][1])
            elif node_name == "time_of_week":
                time_of_week = constructor.construct_scalar(nodes[i][1])

        if seconds is None and time_of_week is None:
            raise ValueError("The YAML file lacked both a time_of_week and a seconds")
        if seconds is not None and time_of_week is not None:
            raise ValueError(
                "YAML file defines both time_of_week and seconds (incompatible)"
            )
        elif time_of_week is not None and femtoseconds is not None:
            raise ValueError(
                "YAML file defines both time_of_week and femtoseconds (incompatible)"
            )
        elif seconds is not None and femtoseconds is None:
            seconds, femtoseconds = _tow2sec(float(seconds))
        elif time_of_week is not None:
            seconds, femtoseconds = _tow2sec(float(time_of_week))

        return cls(int(week_number), int(seconds), int(femtoseconds))

    def to_datetime(self) -> datetime.datetime:
        """Convert the `GPSTime` to a datetime.

        This method calls `tow2datetime()` to convert the `GPSTime` to a
        datetime object.

        Returns
        -------
        datetime.datetime
            The equivalent datetime representation of the `GPSTime`

        Notes
        -----
        .. note::
            Datetimes are limited to microsecond resolution, so this
            conversion may lose some fidelity.

        """
        return tow2datetime(self.week_number, self.time_of_week)

    @classmethod
    def from_datetime(cls, time: datetime.datetime) -> GPSTime:
        """Create a `GPSTime` for a datetime.

        Parameters
        ----------
        time : datetime.datetime
            The datetime that will be converted to a `GPSTime`

        Returns
        -------
        GPSTime
            The `GPSTime` corresponding to the datetime. This is a lossless
            conversion.
        """ 

        """
        Raises
        ------
        TypeError
            If the input value is not a datetime

        Notes
        -----
        This is a classmethod and thus can be called without instantiating the
        object first.

        """
        if not isinstance(time, datetime.datetime):
            raise TypeError("time must be a datetime")

        week_num, tow = datetime2tow(time)

        return cls(week_num, tow)

    def to_zcount(self) -> float:
        """Get the current Z-Count.

        Returns
        -------
        float
            The time of week divided by 1.5

        """
        return self.time_of_week / 1.5

    def correct_weeks(self) -> None:
        """Correct the week number based on the time of week.

        If the time of week is less than 0 or greater than 604800 seconds,
        then the week number and time of week will be corrected to ensure that
        the time of week is within the week indicated by the week number.

        Returns
        -------
        None

        """
        logger.warning(
            "The correct_weeks() method will be deprecated in a future version. Use the correct_time() method instead."
        )
        if (self.time_of_week >= _SEC_IN_WEEK) or (self.time_of_week < 0):
            weeks_to_add = int(self.time_of_week // _SEC_IN_WEEK)
            new_time_of_week = float(self.time_of_week % _SEC_IN_WEEK)

            self.week_number += weeks_to_add
            self.time_of_week = new_time_of_week
        else:
            pass

    def correct_time(self) -> None:
        if (self.femtoseconds >= _SEC_TO_FEMTO_SEC) or (self.femtoseconds < 0):
            seconds_to_add = int(self.femtoseconds // _SEC_TO_FEMTO_SEC)
            new_femto_sec = int(self.femtoseconds % _SEC_TO_FEMTO_SEC)

            self.seconds += seconds_to_add
            self.femtoseconds = new_femto_sec

        if (self.seconds >= _SEC_IN_WEEK) or (self.seconds < 0):
            weeks_to_add = int(self.seconds // _SEC_IN_WEEK)
            new_sec = int(self.seconds % _SEC_IN_WEEK)

            self.week_number += weeks_to_add
            self.seconds = new_sec

    def __add__(
        self,
        other: Union[
            int, float, GPSTime, datetime.datetime, datetime.timedelta, np.ndarray
        ],
    ) -> Union[GPSTime, np.ndarray]:
        """Addition, apply an offset to a `GPSTime`.

        This is the addition of a `GPSTime` and another object. In this
        context, addition means moving the clock of the first argument
        forward by some amount.

        Suppose `a` is a `GPSTime` and the value give for other represents a
        positive time. The value returned will be a `GPSTime` object that is
        the amount of time represented by other after `a`.

        Parameters
        ----------
        other : Union[int, float, GPSTime, datetime.datetime,
                      datetime.timedelta, np.ndarray]
            The other value to add to the `GPSTime`. `int` and `float` values
            are the number of seconds to add to the `GPSTime`. `GPSTime` and
            `datetime.timedelta` have explicit unit definitions that are used.
             If the value is a datetime.datetime, it is converted to a GPSTime
             before adding.

        Returns
        -------
        Union[GPSTime, np.ndarray]
            The sum of the `GPSTime` and `other`. If other is an np.array,
            returns the sum for each element
        """

        """
        Raises
        ------
        TypeError
            If other is not a supported type

        Notes
        -----
        .. note::
            Apart from adding of `datetime.timedelta` objects, this
            functionality does not exist with datetimes.

        .. note::
            This function can be used to "add" a negative amount of time,
            which can yield different results than subtraction.

        """
        if isinstance(other, bool):
            raise TypeError(
                "unsupported operand type(s) for -: '{}' and '{}'".format(
                    type(self), type(other)
                )
            )
        if isinstance(other, int) or isinstance(other, float):
            gps_time_to_add = GPSTime(0, float(other))
        elif isinstance(other, datetime.timedelta):
            gps_time_to_add = GPSTime(0, other.total_seconds())
        elif isinstance(other, datetime.datetime):
            gps_time_to_add = GPSTime.from_datetime(other)
        elif isinstance(other, GPSTime):
            gps_time_to_add = other
        elif isinstance(other, np.ndarray):
            input = np.array([self])
            return input + other
        else:
            raise TypeError(
                "unsupported operand type(s) for +: '{}' and '{}'".format(
                    type(self), type(other)
                )
            )

        week_num = self.week_number + gps_time_to_add.week_number
        seconds = self.seconds + gps_time_to_add.seconds
        femtoseconds = self.femtoseconds + gps_time_to_add.femtoseconds
        return GPSTime(week_num, seconds, femtoseconds)

    def __sub__(
        self,
        other: Union[
            int, float, GPSTime, datetime.datetime, datetime.timedelta, np.ndarray
        ],
    ) -> Union[GPSTime, float, np.ndarray]:
        """Subtraction.

        This method is used to represent subtraction. Depending on the type of
        the arguments, it can be used to find the time offset by an amount or
        the number of seconds between two times.

        Parameters
        ----------
        other : Union[int, float, GPSTime, datetime.datetime,
                      datetime.timedelta, np.ndarray]
            The other value to subtract from the `GPSTime`. `int` and `float`
            values are the number of seconds to subtract from the `GPSTime`.
            `GPSTime` and `datetime.timedelta` have explicit unit definitions
            that are used. If the value is a datetime.datetime, it is
            converted to a GPSTime before subtracting.

        Returns
        -------
        Union[GPSTime, float, np.ndarray]
            A float will be return if both values are `GPSTime` objects that
            represents the number of seconds between the objects. A GPSTime
            will be returned otherwise and it represents offsetting the time
            backward by the amount given. If the input is an np.ndarray, then
            returns the operation for each element

            Notes
            -----
            Subtracting a non-`GPSTime` object is equivalent to adding the opposite
            of its value
        """
        
        """
        Raises
        ------
        TypeError
            If other is not a supported type


        """
        if isinstance(other, bool):
            raise TypeError(
                "unsupported operand type(s) for -: '{}' and '{}'".format(
                    type(self), type(other)
                )
            )
        if isinstance(other, int) or isinstance(other, float):
            sec_to_sub, femto_to_sub = _tow2sec(float(other))

            return GPSTime(
                self.week_number,
                self.seconds - sec_to_sub,
                self.femtoseconds - femto_to_sub,
            )

        elif isinstance(other, datetime.timedelta):
            sec_to_sub, femto_to_sub = _tow2sec(float(other.total_seconds()))

            return GPSTime(
                self.week_number,
                self.seconds - sec_to_sub,
                self.femtoseconds - femto_to_sub,
            )

        elif isinstance(other, datetime.datetime):
            other_gpstime = GPSTime.from_datetime(other)

            weeks_diff = self.week_number - other_gpstime.week_number
            sec_diff = self.seconds - other_gpstime.seconds
            femto_diff = self.femtoseconds - other_gpstime.femtoseconds

            return float(
                weeks_diff * _SEC_IN_WEEK + sec_diff + femto_diff * _FEMTO_SEC_TO_SEC
            )

        elif isinstance(other, GPSTime):
            weeks_diff = self.week_number - other.week_number
            sec_diff = self.seconds - other.seconds
            femto_diff = self.femtoseconds - other.femtoseconds

            return float(
                weeks_diff * _SEC_IN_WEEK + sec_diff + femto_diff * _FEMTO_SEC_TO_SEC
            )

        elif isinstance(other, np.ndarray):
            if other.dtype == np.object:
                _type = np.reshape(other, sum([i for i in other.shape]))[0].__class__

                if _type in (self.__class__, datetime.datetime):
                    input = np.array([self])
                    return np.array(input - other, dtype=float)
                elif _type is datetime.timedelta:
                    input = np.array([self])
                    return np.array(input - other, dtype=object)
            elif other.dtype in (
                int,
                float,
            ):
                input = np.array([self])
                return np.array(input - other, dtype=object)

        else:
            raise TypeError(
                "unsupported operand type(s) for -: '{}' and '{}'".format(
                    type(self), type(other)
                )
            )

    def __lt__(self, other: Union[GPSTime, datetime.datetime]) -> bool:
        """Comparison: Less Than.

        .. note:: In this context "less than" is equivalent to "before"

        Parameters
        ----------
        other : Union[GPSTime, datetime.datetime]
            The object to compare. Datatimes will be converted to `GPSTime`

        Returns
        -------
        bool
            True if the current object is before its comparison
        """
        
        """
        Raises
        ------
        TypeError
            If an invalid type

        """
        if isinstance(other, datetime.datetime):
            other_time = GPSTime.from_datetime(other)
        elif isinstance(other, GPSTime):
            other_time = other
        else:
            raise TypeError(
                "'<' not supported between instances of '{}' and '{}'".format(
                    type(self), type(other)
                )
            )
        return (self - other_time) < 0

    def __gt__(self, other: Union[GPSTime, datetime.datetime]) -> bool:
        """Comparison: Greater Than.

        .. note:: In this context "greater than" is equivalent to "after"

        Parameters
        ----------
        other : Union[GPSTime, datetime.datetime]
            The object to compare. Datatimes will be converted to `GPSTime`

        Returns
        -------
        bool
            True if the current object is after its comparison
        """
        
        """
        Raises
        ------
        TypeError
            If an invalid type

        """
        if isinstance(other, datetime.datetime):
            other_time = GPSTime.from_datetime(other)
        elif isinstance(other, GPSTime):
            other_time = other
        else:
            raise TypeError(
                "'>' not supported between instances of '{}' and '{}'".format(
                    type(self), type(other)
                )
            )
        return (self - other_time) > 0

    def __eq__(self, other: Union[GPSTime, datetime.datetime]) -> bool:
        """Comparison: Equality.

        .. note:: In this context "equality" is equivalent to "coincident"

        Parameters
        ----------
        other : Union[GPSTime, datetime.datetime]
            The object to compare. Datatimes will be converted to `GPSTime`

        Returns
        -------
        bool
            True if the current object is the same time as its comparison
        """
        
        """
        Raises
        ------
        TypeError
            If an invalid type

        """
        if isinstance(other, datetime.datetime):
            other_time = GPSTime.from_datetime(other)
        elif isinstance(other, GPSTime):
            other_time = other
        else:
            raise TypeError(
                "'>' not supported between instances of '{}' and '{}'".format(
                    type(self), type(other)
                )
            )
        return (self - other_time) == 0

    def __le__(self, other: Union[GPSTime, datetime.datetime]) -> bool:
        """Comparison: Less Than or Equals.

        Calls the `__lt__()` and `__eq__()` methods

        Parameters
        ----------
        other : Union[GPSTime, datetime.datetime]
            The object to compare. Datatimes will be converted to `GPSTime`

        Returns
        -------
        bool
            True if the current object is before or at the same time as its
            comparison object.
        """
        
        """
        Raises
        ------
        TypeError
            If an invalid type

        """
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other: Union[GPSTime, datetime.datetime]) -> bool:
        """Comparison: Greater Than or Equals.

        Calls the `__gt__()` and `__eq__()` methods

        Parameters
        ----------
        other : Union[GPSTime, datetime.datetime]
            The object to compare. Datatimes will be converted to `GPSTime`

        Returns
        -------
        bool
            True if the current object is after or at the same time as its
            comparison object.
        """
        
        """        
        Raises
        ------
        TypeError
            If an invalid type

        """
        return self.__gt__(other) or self.__eq__(other)

    def __ne__(self, other: Union[GPSTime, datetime.datetime]) -> bool:
        """Comparison: Not Equals.

        Inverts the result of the `__eq__()` method

        Parameters
        ----------
        other : Union[GPSTime, datetime.datetime]
            The object to compare. Datatimes will be converted to `GPSTime`

        Returns
        -------
        bool
            True if the current object is not the same time as its comparison
        """
        
        """
        Raises
        ------
        TypeError
            If an invalid type

        """
        return not (self.__eq__(other))

    def __hash__(self):
        """Make GPSTime hashable."""
        return hash(str(self.week_number) + str(self.seconds) + str(self.femtoseconds))

    def __repr__(self) -> str:
        """Representation of the object.

        Returns
        -------
        str
            The representation of the object

        """
        return "GPSTime(week_number={}, time_of_week={})".format(
            self.week_number, self.time_of_week
        )
