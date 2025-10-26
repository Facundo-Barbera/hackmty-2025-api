"""
Drawer Status API endpoints - CRITICAL: Includes batch stacking detection.
"""
from flask import Blueprint, request
from app import db
from app.models import DrawerStatus, DrawerStatusEnum, Drawer, ItemBatch, DrawerBatchTracking
from app.services.batch_tracking import create_drawer_status_with_batch, mark_batch_depleted
from app.utils.responses import success_response, error_response, warning_response
from app.utils.validators import validate_uuid, validate_required_fields
from datetime import datetime

bp = Blueprint('drawer_status', __name__, url_prefix='/api/drawer-status')


@bp.route('', methods=['POST'])
def create_status():
    """
    Create new drawer status with batch tracking
    ---
    tags:
      - Drawer Status
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - drawer_id
            - batch_id
            - quantity
            - status
          properties:
            drawer_id:
              type: string
              description: UUID of the drawer
              example: "123e4567-e89b-12d3-a456-426614174000"
            batch_id:
              type: string
              description: UUID of the item batch
              example: "223e4567-e89b-12d3-a456-426614174000"
            quantity:
              type: integer
              description: Quantity loaded into drawer
              example: 24
            status:
              type: string
              enum: [empty, partial, full, needs_restock]
              description: Drawer status
              example: "full"
            employee_id:
              type: string
              description: Optional UUID of employee performing action
              example: "323e4567-e89b-12d3-a456-426614174000"
    responses:
      201:
        description: Status created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
      207:
        description: "CRITICAL: Status created but batch stacking detected - WARNING issued"
        schema:
          type: object
          properties:
            status:
              type: string
              example: warning
            data:
              type: object
            warning:
              type: object
              properties:
                code:
                  type: string
                  example: BATCH_STACKING_DETECTED
                message:
                  type: string
                  example: "Warning: Loading batch over 2 non-depleted batch(es)"
                non_depleted_batches:
                  type: array
                  items:
                    type: object
      400:
        description: Validation error
      404:
        description: Drawer or batch not found
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        validate_required_fields(data, ['drawer_id', 'batch_id', 'quantity', 'status'])

        # Validate UUIDs
        drawer_uuid = validate_uuid(data['drawer_id'], 'drawer_id')
        batch_uuid = validate_uuid(data['batch_id'], 'batch_id')

        # Validate drawer and batch exist
        drawer = Drawer.query.get(drawer_uuid)
        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {data["drawer_id"]} not found', status_code=404)

        batch = ItemBatch.query.get(batch_uuid)
        if not batch:
            return error_response('NOT_FOUND', f'Batch {data["batch_id"]} not found', status_code=404)

        # Validate status
        status_enum = DrawerStatusEnum(data['status'])

        # Get employee_id if provided
        employee_uuid = None
        if 'employee_id' in data:
            employee_uuid = validate_uuid(data['employee_id'], 'employee_id')

        # Use batch tracking service (handles stacking detection)
        drawer_status, warning = create_drawer_status_with_batch(
            drawer_id=drawer_uuid,
            batch_id=batch_uuid,
            quantity=int(data['quantity']),
            status_value=status_enum,
            employee_id=employee_uuid
        )

        # Return with warning if batch stacking detected
        if warning:
            return warning_response(drawer_status, warning, status_code=207)

        return success_response(drawer_status, status_code=201)

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('', methods=['GET'])
def list_statuses():
    """
    List all drawer statuses
    ---
    tags:
      - Drawer Status
    responses:
      200:
        description: List of all drawer statuses
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
        statuses = DrawerStatus.query.all()
        return success_response(statuses)

    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/drawer/<drawer_id>', methods=['GET'])
def get_status_by_drawer(drawer_id):
    """
    Get current status for a specific drawer
    ---
    tags:
      - Drawer Status
    parameters:
      - in: path
        name: drawer_id
        type: string
        required: true
        description: UUID of the drawer
    responses:
      200:
        description: Current drawer status
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
      400:
        description: Invalid UUID format
      404:
        description: No status found for drawer
      500:
        description: Server error
    """
    try:
        drawer_uuid = validate_uuid(drawer_id, 'drawer_id')

        # Get the most recent status for this drawer
        status = DrawerStatus.query.filter_by(drawer_id=drawer_uuid).order_by(
            DrawerStatus.last_updated.desc()
        ).first()

        if not status:
            return error_response('NOT_FOUND', f'No status found for drawer {drawer_id}', status_code=404)

        return success_response(status)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<status_id>', methods=['PUT'])
def update_status(status_id):
    """
    Update drawer status
    ---
    tags:
      - Drawer Status
    parameters:
      - in: path
        name: status_id
        type: string
        required: true
        description: UUID of the drawer status
      - in: body
        name: body
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [empty, partial, full, needs_restock]
              description: Updated status value
    responses:
      200:
        description: Status updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
      400:
        description: Validation error
      404:
        description: Drawer status not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(status_id)
        status = DrawerStatus.query.get(uuid_id)

        if not status:
            return error_response('NOT_FOUND', f'Drawer status {status_id} not found', status_code=404)

        data = request.get_json()

        # Update fields if provided
        if 'status' in data:
            status.status = DrawerStatusEnum(data['status'])

        status.last_updated = datetime.utcnow()
        db.session.commit()

        return success_response(status)

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<status_id>', methods=['DELETE'])
def delete_status(status_id):
    """
    Delete drawer status
    ---
    tags:
      - Drawer Status
    parameters:
      - in: path
        name: status_id
        type: string
        required: true
        description: UUID of the drawer status
    responses:
      200:
        description: Status deleted successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                message:
                  type: string
                  example: Drawer status deleted successfully
      400:
        description: Invalid UUID format
      404:
        description: Drawer status not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(status_id)
        status = DrawerStatus.query.get(uuid_id)

        if not status:
            return error_response('NOT_FOUND', f'Drawer status {status_id} not found', status_code=404)

        db.session.delete(status)
        db.session.commit()

        return success_response({'message': 'Drawer status deleted successfully'})

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<status_id>/deplete-batch', methods=['POST'])
def deplete_batch(status_id):
    """
    Mark a batch as depleted
    ---
    tags:
      - Drawer Status
    parameters:
      - in: path
        name: status_id
        type: string
        required: true
        description: UUID of the drawer status
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - batch_tracking_id
          properties:
            batch_tracking_id:
              type: string
              description: UUID of the batch tracking record
              example: "423e4567-e89b-12d3-a456-426614174000"
    responses:
      200:
        description: Batch marked as depleted successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
      400:
        description: Validation error
      404:
        description: Batch tracking not found
      500:
        description: Server error
    """
    try:
        status_uuid = validate_uuid(status_id)
        data = request.get_json()

        # Validate required fields
        validate_required_fields(data, ['batch_tracking_id'])

        tracking_uuid = validate_uuid(data['batch_tracking_id'], 'batch_tracking_id')

        # Use service to mark batch as depleted
        tracking = mark_batch_depleted(tracking_uuid)

        if not tracking:
            return error_response('NOT_FOUND', f'Batch tracking {data["batch_tracking_id"]} not found', status_code=404)

        return success_response(tracking)

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<status_id>/batches', methods=['GET'])
def list_batches_in_drawer(status_id):
    """
    List all batches in a drawer status
    ---
    tags:
      - Drawer Status
    parameters:
      - in: path
        name: status_id
        type: string
        required: true
        description: UUID of the drawer status
    responses:
      200:
        description: List of all batch trackings
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
      400:
        description: Invalid UUID format
      404:
        description: Drawer status not found
      500:
        description: Server error
    """
    try:
        status_uuid = validate_uuid(status_id)

        # Check if status exists
        status = DrawerStatus.query.get(status_uuid)
        if not status:
            return error_response('NOT_FOUND', f'Drawer status {status_id} not found', status_code=404)

        # Get all batch trackings
        trackings = DrawerBatchTracking.query.filter_by(drawer_status_id=status_uuid).all()

        return success_response(trackings)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<status_id>/non-depleted-batches', methods=['GET'])
def list_non_depleted_batches(status_id):
    """
    List non-depleted batches (for checking batch stacking warnings)
    ---
    tags:
      - Drawer Status
    parameters:
      - in: path
        name: status_id
        type: string
        required: true
        description: UUID of the drawer status
    responses:
      200:
        description: List of non-depleted batch trackings
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
      400:
        description: Invalid UUID format
      404:
        description: Drawer status not found
      500:
        description: Server error
    """
    try:
        status_uuid = validate_uuid(status_id)

        # Check if status exists
        status = DrawerStatus.query.get(status_uuid)
        if not status:
            return error_response('NOT_FOUND', f'Drawer status {status_id} not found', status_code=404)

        # Get non-depleted batches
        trackings = DrawerBatchTracking.query.filter_by(
            drawer_status_id=status_uuid,
            is_depleted=False
        ).all()

        return success_response(trackings)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)
