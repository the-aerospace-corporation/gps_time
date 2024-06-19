# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/11_logutils.ipynb.

# %% auto 0
__all__ = ['display_distro_statement', 'Colors', 'ThemeField', 'color_text', 'BasicTheme', 'BasicColorTheme',
           'AlignedColorFormatter']

# %% ../nbs/11_logutils.ipynb 2
"""Copyright 2020 The Aerospace Corporation"""

# %% ../nbs/11_logutils.ipynb 5
import os
import logging

# %% ../nbs/11_logutils.ipynb 6
def display_distro_statement(
    msg: str, logger: logging.Logger, level: str = "critical"
) -> None:
    """Display a distro statement

    The purpose of this method is to produce a distribution statement in the
    logger messages. This statement is separated by a line before and after
    and the message is surrounded by asterisks.

    Parameters
    ----------
    msg : str
        The distribution statement
    logger : logging.Logger
        The logger that will be used
    level : str
        The logging level. Valid values are 'critical', 'error', 'warning',
        'info', and 'debug'. By default 'critical'.

    """
    if level.lower() in ("critical", "error", "warning", "info", "debug"):
        logger_method = getattr(logger, level.lower())
    else:
        ValueError(f"Invalid Logging Level for Distro Statement: {level}")

    msg_str = "*** " + msg + " ***"

    logger_method(" ")
    logger_method("*" * len(msg_str))
    logger_method(msg_str)
    logger_method("*" * len(msg_str))
    logger_method(" ")

# %% ../nbs/11_logutils.ipynb 7
class Colors:
    """Data structure containing color codes.

    Data structure containing character codes which change text color of a
    bash terminal of all following characters.

    Class Attributes
    ----------------
    normal : str
        Resets text colors in the terminal to default colors
    black : str
        Sets text color in terminal to black
    red : str
        Sets text color in terminal to red
    green : str
        Sets text color in terminal to green
    yellow : str
        Sets text color in terminal to yellow
    blue : str
        Sets text color in terminal to blue
    purple : str
        Sets text color in terminal to purple
    cyan : str
        Sets text color in terminal to cyan
    white : str
        Sets text color in terminal to white
    red_highlight : str
        Sets text background color to red
    green_highlight : str
        Sets text background color to green
    yellow_highlight : str
        Sets text background color to yellow
    blue_highlight : str
        Sets text background color to blue
    purple_highlight : str
        Sets text background color to purple
    cyan_highlight : str
        Sets text background color to cyan
    white_highlight : str
        Sets text background color to white
    bold : str
        Sets text thickness larger
    uline : str
        Adds an underline to text
    blink : str
        Makes the text blink at 1Hz
    invert : str
        Inverts the background and text colors
    """

    normal = "\033[0m"
    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    purple = "\033[35m"
    cyan = "\033[36m"
    white = "\033[37m"

    red_highlight = "\033[41m"
    green_highlight = "\033[42m"
    yellow_highlight = "\033[43m"
    blue_highlight = "\033[44m"
    purple_highlight = "\033[45m"
    cyan_highlight = "\033[46m"
    white_highlight = "\033[47m"

    bold = "\033[1m"
    uline = "\033[4m"
    blink = "\033[5m"
    invert = "\033[7m"

# %% ../nbs/11_logutils.ipynb 8
class ThemeField(object):
    """
    Various components of a log can have colors edited such as the prompt,
    message, etc. A message field maps the colors to various log levels
    and indexed using logging levels.

    Attributes
    ----------
    DEBUG: str
        Str color code defined in Colors class for correcsponding log level
    INFO: str
        Str color code defined in Colors class for correcsponding log level
    WARNING: str
        Str color code defined in Colors class for correcsponding log level
    ERROR: str
        Str color code defined in Colors class for correcsponding log level
    CRITICAL: str
        Str color code defined in Colors class for correcsponding log level

    Examples
    --------
        >> field = ThemeField(DEBUG=Colors.green,
                              INFO=Colors.white,
                              WARNING=Colors.yellow,
                              ERROR=Colors.purple,
                              CRITICAL=Colors.red)
    """

    def __init__(self, DEBUG, INFO, WARNING, ERROR, CRITICAL):
        """
        Initializes logging levels to a color

        Parameters
        ----------
        DEBUG:
            Str color code defined in colors class for corresponding log level
        INFO:
            Str color code defined in colors class for corresponding log level
        WARNING:
            Str color code defined in colors class for corresponding log level
        ERROR:
            Str color code defined in colors class for corresponding log level
        CRITICAL:
            Str color code defined in colors class for corresponding log level
        """
        self.DEBUG = DEBUG
        self.INFO = INFO
        self.WARNING = WARNING
        self.ERROR = ERROR
        self.CRITICAL = CRITICAL

    def __getitem__(self, item: str) -> str:
        """
        Gets an attribute using [] indexing. In logging formatters record.level
        is a string which can be used to index this class.

        Parameters
        ----------
        item: str
            Formatter record.level to return value for

        Returns
        -------
        str
            Color code for corresponding log level
        """
        return getattr(self, item)

    def __setitem__(self, key: str, value: str) -> None:
        """
        Sets a color value using [] = indexing to change value with Formatter
        record.level

        Parameters
        ----------
        key: str
            Formatter record.level or string matching attribute name
        value: str
            New color code to set the level to
        """
        setattr(self, key, value)

# %% ../nbs/11_logutils.ipynb 9
def color_text(text: str, *colors: str):
    """
    Applies color to a specific string and appends the color code to set the
    text to normal. Text can be various colors by adding more args for colors.

    Parameters
    ----------
    text: str
        String to color
    colors: Tuple[str]
        Any amount of color codes

    Returns
    -------
    str
        Input string with each color in colors prepended to the string in
        order with a Colors.normal trailing.
    """
    color = ""
    for c in colors:
        color += c
    if os.name == "nt":  # Windows (bleh)
        return text
    else:
        return color + text + Colors.normal

# %% ../nbs/11_logutils.ipynb 10
class BasicTheme(object):
    """
    The base object used in applying themes. A theme is just a collection of
    ThemeField objects for different portions of the output log. This class
    is meant to be inherited from for other themes and the desired fields
    overwritten with new colors.

    Class Attributes
    ----------------
    Themes
        A list of every theme. This allows for themes to be gotten globally.
    """

    THEMES = []

    @classmethod
    def get_theme(cls, name):
        """
        Everytime a theme is instantiated its name is added to the THEMES
        class attribute. This name is used to access any theme defined in
        runtime by a common theme.

        Parameters
        ----------
        name: str
            Name of theme to be indexed

        Returns
        -------
        Optional[BasicTheme]
            Theme corresponding to input name. If no theme by that name exists
            None is returned.
        """
        for theme in BasicTheme.THEMES:
            if theme == name:
                return theme

    def __init__(self, theme_name: str) -> None:
        """
        Creates a theme and adds the theme to the THEMES class attribute for
        later indexing.

        Parameters
        ----------
        theme_name: str
            Name of the theme

        Attributes
        ----------
        name: str
             The name of the theme
        prompt: str
             First character(s) before the log message
        tail: str
             Final characters in the log message
        level_color: ThemeField
             The color of the log level text displayed in the message
        text_color: ThemeField
            The color of the text displayed at each logging level
        """
        # if theme_name in BasicTheme.THEMES:
        #     raise ValueError("Theme {} already exists".format(theme_name))
        self.name = theme_name
        self.prompt = ThemeField(*([">>"] * 5))
        self.tail = ThemeField(*([""] * 5))
        self.level_color = ThemeField(
            DEBUG=Colors.green,
            INFO=Colors.white,
            WARNING=Colors.yellow,
            ERROR=Colors.purple,
            CRITICAL=Colors.red,
        )
        self.text_color = ThemeField(
            DEBUG=Colors.normal,
            INFO=Colors.normal,
            WARNING=Colors.normal,
            ERROR=Colors.normal,
            CRITICAL=Colors.normal,
        )
        BasicTheme.THEMES.append(self)

    def __eq__(self, other_name: str) -> bool:
        """
        Compares the name of self to a string and determines if the two
        are the same using == operator.

        Parameters
        ----------
        other_name: str
            Name of other theme

        Returns
        -------
        bool
            True if self.name is equal to the other name (case-sensitive)
        """
        return self.name == other_name

# %% ../nbs/11_logutils.ipynb 11
class BasicColorTheme(BasicTheme):
    """
    Theme for basic colored output where the logging level text is the same
    color as the log message. This class is a good example for how to create
    new themes by inheriting from the basic theme. The derived themes if any
    field is not overwritten just stays the same as the default one.
    """

    def __init__(self, theme_name="color_theme"):
        """
        Instantiates the theme.

        Parameters
        ----------
        theme_name: str
            Name of the theme

        Attributes
        ----------
        name: str
             The name of the theme
        prompt: str
             First character(s) before the log message
        tail: str
             Final characters in the log message
        level_color: ThemeField
             The color of the log level text displayed in the message. In this
             case [green, white, yellow, purple, red] from DEBUG to CRITICAL
        text_color: ThemeField
            The color of the text displayed at each logging level. Same
            colors as level name
        theme_name
        """
        super().__init__(theme_name)
        self.prompt = ThemeField(*([">>"] * 5))
        self.text_color = ThemeField(
            DEBUG=Colors.green,
            INFO=Colors.white,
            WARNING=Colors.yellow,
            ERROR=Colors.purple,
            CRITICAL=Colors.red,
        )

# %% ../nbs/11_logutils.ipynb 12
class AlignedColorFormatter(logging.Formatter):
    """
    Logging formatter to display aligned meta data of date with ms time stamp,
    logger name, line number, and log level.
    """

    width = 24
    datefmt = "%I:%M:%S"

    def __init__(self, theme: BasicTheme) -> None:
        """
        Creates the formatted text described and applies a theme to the text.

        Parameters
        ----------
        theme: BasicTheme
            Theme derived from basic theme to apply to text
        """
        super().__init__()
        self.theme = theme

    def format(self, record: logging.LogRecord) -> str:
        """
        Applies the desired format to a string passed to one of the log messages.

        Parameters
        ----------
        record: logging.LogRecord
            Data structure containing various log parameters.

        Returns
        -------
        str
            String with applied format and theme
        """
        record.message = record.getMessage()
        level = color_text(record.levelname, self.theme.level_color[record.levelname])
        s = "%s.%03d :: %+50s :: %-4s :: %-19s | %s " % (
            self.formatTime(record, AlignedColorFormatter.datefmt),
            record.msecs,
            record.name,
            record.lineno,
            level,
            self.theme.prompt[record.levelname],
        )
        s += color_text(record.message, self.theme.text_color[record.levelname])

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                if s[-1:] != "\n":
                    s = s + "\n"
                s = s + record.exc_text
        return s
