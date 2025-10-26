"""
Drawers API endpoints.
"""
from flask import Blueprint, request, Response
from app import db
from app.models import Drawer
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_uuid, validate_required_fields, validate_positive_integer
from app.utils.qr_codes import qr_png_data_uri, qr_png_bytes
from datetime import datetime

bp = Blueprint('drawers', __name__, url_prefix='/api/drawers')


@bp.route('', methods=['POST'])
def create_drawer():
    """
    Create a new drawer
    ---
    tags:
      - Drawers
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - drawer_code
            - trolley_id
            - position
            - capacity
            - drawer_type
          properties:
            drawer_code:
              type: string
              description: Unique drawer identifier
              example: "DR-A1"
            trolley_id:
              type: string
              description: Trolley identifier
              example: "TROLLEY-001"
            position:
              type: integer
              description: Drawer position in trolley
              example: 1
            capacity:
              type: integer
              description: Maximum capacity
              example: 50
            drawer_type:
              type: string
              description: Type of drawer (cold, ambient, etc.)
              example: "cold"
    responses:
      201:
        description: Drawer created successfully
      400:
        description: Validation error
      409:
        description: Duplicate drawer code
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        validate_required_fields(data, ['drawer_code', 'trolley_id', 'position', 'capacity', 'drawer_type'])

        # Check if drawer_code already exists
        existing = Drawer.query.filter_by(drawer_code=data['drawer_code']).first()
        if existing:
            return error_response('DUPLICATE_DRAWER', f'Drawer code {data["drawer_code"]} already exists', status_code=409)

        # Create drawer
        drawer = Drawer(
            drawer_code=data['drawer_code'],
            trolley_id=data['trolley_id'],
            position=validate_positive_integer(data['position'], 'position', allow_zero=True),
            capacity=validate_positive_integer(data['capacity'], 'capacity'),
            drawer_type=data['drawer_type']
        )

        db.session.add(drawer)
        db.session.commit()

        return success_response(drawer, status_code=201)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('', methods=['GET'])
def list_drawers():
    """
    List all drawers
    ---
    tags:
      - Drawers
    responses:
      200:
        description: List of all drawers
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                type: object
      500:
        description: Server error
    """
    try:
        drawers = Drawer.query.all()
        return success_response(drawers)

    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<drawer_id>', methods=['GET'])
def get_drawer(drawer_id):
    """
    Get a specific drawer by ID
    ---
    tags:
      - Drawers
    parameters:
      - in: path
        name: drawer_id
        type: string
        required: true
        description: UUID of the drawer
    responses:
      200:
        description: Drawer details
      400:
        description: Invalid UUID format
      404:
        description: Drawer not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(drawer_id)
        drawer = Drawer.query.get(uuid_id)

        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {drawer_id} not found', status_code=404)

        return success_response(drawer)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<drawer_id>', methods=['PUT'])
def update_drawer(drawer_id):
    """
    Update a drawer
    ---
    tags:
      - Drawers
    parameters:
      - in: path
        name: drawer_id
        type: string
        required: true
        description: UUID of the drawer
      - in: body
        name: body
        schema:
          type: object
          properties:
            trolley_id:
              type: string
            position:
              type: integer
            capacity:
              type: integer
            drawer_type:
              type: string
    responses:
      200:
        description: Drawer updated successfully
      400:
        description: Validation error
      404:
        description: Drawer not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(drawer_id)
        drawer = Drawer.query.get(uuid_id)

        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {drawer_id} not found', status_code=404)

        data = request.get_json()

        # Update fields if provided
        if 'trolley_id' in data:
            drawer.trolley_id = data['trolley_id']
        if 'position' in data:
            drawer.position = validate_positive_integer(data['position'], 'position', allow_zero=True)
        if 'capacity' in data:
            drawer.capacity = validate_positive_integer(data['capacity'], 'capacity')
        if 'drawer_type' in data:
            drawer.drawer_type = data['drawer_type']

        drawer.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response(drawer)

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<drawer_id>', methods=['DELETE'])
def delete_drawer(drawer_id):
    """
    Delete a drawer
    ---
    tags:
      - Drawers
    parameters:
      - in: path
        name: drawer_id
        type: string
        required: true
        description: UUID of the drawer
    responses:
      200:
        description: Drawer deleted successfully
      400:
        description: Invalid UUID format
      404:
        description: Drawer not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(drawer_id)
        drawer = Drawer.query.get(uuid_id)

        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {drawer_id} not found', status_code=404)

        db.session.delete(drawer)
        db.session.commit()

        return success_response({'message': 'Drawer deleted successfully'})

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<drawer_id>/qr-code', methods=['POST'])
def generate_drawer_qr(drawer_id):
    """
    Generate a QR code for a drawer.
    ---
    tags:
      - Drawers
    parameters:
      - in: path
        name: drawer_id
        type: string
        required: true
        description: UUID of the drawer to link with the QR code
    responses:
      201:
        description: QR code generated successfully
      400:
        description: Invalid UUID format
      404:
        description: Drawer not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(drawer_id)
        drawer = Drawer.query.get(uuid_id)

        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {drawer_id} not found', status_code=404)

        payload = str(drawer.id)
        qr_data_uri = qr_png_data_uri(payload)

        drawer.qr_code = payload
        db.session.commit()

        response_payload = {
            'drawer_id': payload,
            'qr_payload': payload,
            'qr_code_image': qr_data_uri
        }

        return success_response(response_payload, status_code=201)

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<drawer_id>/qr-code', methods=['GET'])
def get_drawer_qr(drawer_id):
    """
    Retrieve an existing drawer QR code.
    ---
    tags:
      - Drawers
    parameters:
      - in: path
        name: drawer_id
        type: string
        required: true
        description: UUID of the drawer
    responses:
      200:
        description: Existing QR code
      400:
        description: Invalid UUID format
      404:
        description: Drawer or QR code not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(drawer_id)
        drawer = Drawer.query.get(uuid_id)

        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {drawer_id} not found', status_code=404)

        if not drawer.qr_code:
            return error_response('QR_CODE_NOT_GENERATED', f'Drawer {drawer_id} does not have a QR code yet', status_code=404)

        payload = drawer.qr_code
        qr_data_uri = qr_png_data_uri(payload)

        response_payload = {
            'drawer_id': str(drawer.id),
            'qr_payload': payload,
            'qr_code_image': qr_data_uri
        }

        return success_response(response_payload)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<drawer_id>/qr-code/image', methods=['GET'])
def get_drawer_qr_image(drawer_id):
    """
    Retrieve the QR code image (PNG) for a drawer.
    ---
    tags:
      - Drawers
    parameters:
      - in: path
        name: drawer_id
        type: string
        required: true
        description: UUID of the drawer
    responses:
      200:
        description: PNG image for the QR code
      400:
        description: Invalid UUID format
      404:
        description: Drawer or QR code not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(drawer_id)
        drawer = Drawer.query.get(uuid_id)

        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {drawer_id} not found', status_code=404)

        if not drawer.qr_code:
            return error_response('QR_CODE_NOT_GENERATED', f'Drawer {drawer_id} does not have a QR code yet', status_code=404)

        qr_bytes = qr_png_bytes(drawer.qr_code)
        return Response(qr_bytes, mimetype='image/png')

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)
