"""
Validation utilities for input data.
"""
import uuid
from datetime import datetime


def validate_uuid(value, field_name='id'):
    """
    Validate UUID format.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        UUID: Parsed UUID object

    Raises:
        ValueError: If UUID format is invalid
    """
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        raise ValueError(f'Invalid UUID format for {field_name}')


def validate_date(date_string, field_name='date'):
    """
    Validate ISO 8601 date format.

    Args:
        date_string: Date string to validate
        field_name: Name of the field for error messages

    Returns:
        datetime: Parsed datetime object

    Raises:
        ValueError: If date format is invalid
    """
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        raise ValueError(f'Invalid date format for {field_name}. Expected ISO 8601 format.')


def validate_enum(value, enum_class, field_name='value'):
    """
    Validate enum value.

    Args:
        value: Value to validate
        enum_class: Enum class to validate against
        field_name: Name of the field for error messages

    Returns:
        Enum: Valid enum member

    Raises:
        ValueError: If value is not valid for enum
    """
    try:
        if isinstance(value, enum_class):
            return value
        return enum_class(value)
    except (ValueError, KeyError):
        valid_values = [e.value for e in enum_class]
        raise ValueError(f'Invalid value for {field_name}. Must be one of: {valid_values}')


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present.

    Args:
        data: Dictionary of input data
        required_fields: List of required field names

    Raises:
        ValueError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]

    if missing_fields:
        raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')


def validate_positive_integer(value, field_name='value', allow_zero=False):
    """
    Validate that a value is a positive integer.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        allow_zero: Whether to allow zero as valid

    Returns:
        int: Validated integer

    Raises:
        ValueError: If value is not a positive integer
    """
    try:
        int_value = int(value)
        if allow_zero and int_value < 0:
            raise ValueError(f'{field_name} must be non-negative')
        elif not allow_zero and int_value <= 0:
            raise ValueError(f'{field_name} must be a positive integer')
        return int_value
    except (ValueError, TypeError):
        raise ValueError(f'{field_name} must be an integer')


def validate_numeric_range(value, field_name='value', min_val=None, max_val=None):
    """
    Validate that a numeric value is within a range.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        float: Validated numeric value

    Raises:
        ValueError: If value is outside the range
    """
    try:
        num_value = float(value)
        if min_val is not None and num_value < min_val:
            raise ValueError(f'{field_name} must be at least {min_val}')
        if max_val is not None and num_value > max_val:
            raise ValueError(f'{field_name} must be at most {max_val}')
        return num_value
    except (ValueError, TypeError):
        raise ValueError(f'{field_name} must be a number')
