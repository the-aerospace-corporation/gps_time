import pytest
import logging
import os
from unittest.mock import patch, MagicMock
from gps_time.logutils import (
    display_distro_statement,
    ThemeField,
    Colors,
    BasicTheme,
    BasicColorTheme,
    color_text,
    AlignedColorFormatter
)

def test_display_distro_statement_errors():
    """Test errors and valid paths in display_distro_statement."""
    logger = logging.getLogger("test_logger")
    
    # Test invalid level (raises ValueError)
    with pytest.raises(ValueError, match="Invalid Logging Level"):
        display_distro_statement("msg", logger, level="invalid")
        
    # Test valid level (covers L34, L41-44)
    # mock logger to avoid clutter
    mock_logger = MagicMock()
    display_distro_statement("msg", mock_logger, level="info")
    assert mock_logger.info.call_count == 5

def test_theme_field_methods():
    """Test ThemeField get/set item."""
    tf = ThemeField("D", "I", "W", "E", "C")
    assert tf["DEBUG"] == "D"
    tf["DEBUG"] = "NewD"
    assert tf.DEBUG == "NewD"

def test_color_text_branches():
    """Test color_text on different OS."""
    # Mock os.name to 'posix' to hit color logic
    with patch("os.name", "posix"):
        res = color_text("text", Colors.red)
        assert Colors.red in res
        assert Colors.normal in res
        
    # Mock os.name to 'nt' (Windows)
    with patch("os.name", "nt"):
        res = color_text("text", Colors.red)
        assert res == "text" 

def test_basic_theme_methods():
    """Test BasicTheme methods."""
    # Test __eq__ and get_theme
    t = BasicTheme("my_theme")
    assert t == "my_theme"
    
    # get_theme
    got = BasicTheme.get_theme("my_theme")
    assert got == t
    
    # get_theme non-existent
    assert BasicTheme.get_theme("non_existent") is None

def test_aligned_formatter_exception():
    """Test AlignedColorFormatter with exception info."""
    theme = BasicColorTheme("test_theme")
    fmt = AlignedColorFormatter(theme)
    
    # Create a log record with exception info
    try:
        raise ValueError("test error")
    except ValueError:
        import sys
        exc_info = sys.exc_info()
        
    record = logging.LogRecord(
        name="logger", level=logging.ERROR, pathname="path", lineno=10,
        msg="Error msg", args=(), exc_info=exc_info
    )
    
    # Format
    s = fmt.format(record)
    assert "ValueError: test error" in s
    assert "Error msg" in s
    
    # Test caching (L424) by calling format again
    s2 = fmt.format(record)
    assert s2 == s

def test_basic_color_theme_init():
    """Test BasicColorTheme init."""
    t = BasicColorTheme("new_color_theme")
    assert t.text_color.DEBUG == Colors.green
