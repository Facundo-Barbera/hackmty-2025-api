"""
Response formatting utilities for consistent API responses.
"""
from flask import jsonify
import uuid
from datetime import datetime, date


def success_response(data, status_code=200):
    """
    Format successful API response.

    Args:
        data: Response data (dict, list, or model object)
        status_code: HTTP status code (default 200)

    Returns:
        tuple: (JSON response, status code)
    """
    response = {
        'status': 'success',
        'data': serialize_data(data)
    }
    return jsonify(response), status_code


def error_response(code, message, details=None, status_code=400):
    """
    Format error API response.

    Args:
        code: Error code string
        message: Human-readable error message
        details: Optional additional error details
        status_code: HTTP status code (default 400)

    Returns:
        tuple: (JSON response, status code)
    """
    response = {
        'error': {
            'code': code,
            'message': message
        }
    }

    if details:
        response['error']['details'] = details

    return jsonify(response), status_code


def warning_response(data, warning_dict, status_code=207):
    """
    Format multi-status response with warning (used for batch stacking).

    Args:
        data: Response data
        warning_dict: Warning information with code, message, and details
        status_code: HTTP status code (default 207 Multi-Status)

    Returns:
        tuple: (JSON response, status code)
    """
    response = {
        'status': 'success_with_warning',
        'data': serialize_data(data),
        'warning': warning_dict
    }
    return jsonify(response), status_code


def paginated_response(items, page, per_page, total, status_code=200):
    """
    Format paginated list response.

    Args:
        items: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        status_code: HTTP status code (default 200)

    Returns:
        tuple: (JSON response, status code)
    """
    total_pages = (total + per_page - 1) // per_page  # Ceiling division

    response = {
        'status': 'success',
        'data': serialize_data(items),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages
        }
    }
    return jsonify(response), status_code


def serialize_data(data):
    """
    Serialize data for JSON response, handling UUIDs and datetimes.

    Args:
        data: Data to serialize (dict, list, model, UUID, datetime, etc.)

    Returns:
        Serialized data suitable for JSON response
    """
    if data is None:
        return None

    # Handle model objects with to_dict method
    if hasattr(data, 'to_dict'):
        return data.to_dict()

    # Handle lists
    if isinstance(data, list):
        return [serialize_data(item) for item in data]

    # Handle dictionaries
    if isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}

    # Handle UUID
    if isinstance(data, uuid.UUID):
        return str(data)

    # Handle datetime
    if isinstance(data, datetime):
        return data.isoformat()

    # Handle date
    if isinstance(data, date):
        return data.isoformat()

    # Handle enums
    if hasattr(data, 'value'):
        return data.value

    # Return as-is for basic types
    return data
