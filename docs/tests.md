# Testing

The `gps_time` module includes a comprehensive test suite to ensure accuracy and stability, particularly given the critical nature of time conversions in scientific computing.

## Test Structure

Measurements are validated against known constants and official data sources (e.g., IERS for leap seconds).

| Test File | Description |
| :--- | :--- |
| `test_core.py` | Validates the `GPSTime` class, including initialization, arithmetic operations (add/sub), and comparisons. Ensures femtosecond precision is maintained. |
| `test_datetime.py` | Verifies conversions between `GPSTime`, Python `datetime` objects, and other time formats. Validates `datetime2tow` and `tow2datetime` utilities. |
| `test_leapseconds.py` | Checks the accuracy of leap second data and logic. Includes boundary tests to ensure leap seconds are applied exactly at the transition moment (e.g., June 30, 23:59:60). |
| `test_utilities.py` | Tests helper functions like `arange_gpstime` and validation routines. |

## Running Tests

Tests are written using `pytest`. To run the full suite:

```bash
pytest
```

## Coverage

The test suite covers:
- **Core Logic**: Initialization of `GPSTime` from weeks/seconds, datetimes, and YAML.
- **Arithmetic**: Addition and subtraction of seconds, `timedelta`, and other `GPSTime` objects.
- **Comparisons**: Equality and inequality operators (`<`, `>`, `<=`, `>=`).
- **Leap Seconds**: Historical leap second dates and predictive logic for future dates.
- **Edge Cases**: Week rollovers, negative time adjustments, and picosecond-level precision.
