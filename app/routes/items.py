"""
Items (Batches) API endpoints.
"""
from flask import Blueprint, request
from app import db
from app.models import ItemBatch, BatchStatus
from app.utils.responses import success_response, error_response, paginated_response
from app.utils.validators import validate_uuid, validate_required_fields, validate_positive_integer
from datetime import datetime

bp = Blueprint('items', __name__, url_prefix='/api/items')


@bp.route('', methods=['POST'])
def create_item():
    """
    Create a new item batch
    ---
    tags:
      - Items
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - item_type
            - batch_number
            - quantity
            - expiry_date
          properties:
            item_type:
              type: string
              description: Type of item
              example: "Coca-Cola"
            batch_number:
              type: string
              description: Unique batch identifier
              example: "BATCH-2025-001"
            quantity:
              type: integer
              description: Quantity in batch
              example: 100
            expiry_date:
              type: string
              format: date
              description: Expiry date (ISO 8601)
              example: "2025-12-31"
            received_date:
              type: string
              format: date-time
              description: Optional received date (defaults to current time)
              example: "2025-10-25T10:30:00Z"
            status:
              type: string
              enum: [available, in_use, depleted]
              description: Batch status (defaults to available)
              example: "available"
    responses:
      201:
        description: Batch created successfully
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
      409:
        description: Duplicate batch number
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        validate_required_fields(data, ['item_type', 'batch_number', 'quantity', 'expiry_date'])

        # Check if batch_number already exists
        existing = ItemBatch.query.filter_by(batch_number=data['batch_number']).first()
        if existing:
            return error_response('DUPLICATE_BATCH', f'Batch number {data["batch_number"]} already exists', status_code=409)

        # Create item batch
        item = ItemBatch(
            item_type=data['item_type'],
            batch_number=data['batch_number'],
            quantity=validate_positive_integer(data['quantity'], 'quantity'),
            expiry_date=datetime.fromisoformat(data['expiry_date']).date(),
            received_date=datetime.fromisoformat(data['received_date']) if 'received_date' in data else datetime.utcnow(),
            status=BatchStatus(data.get('status', 'available'))
        )

        db.session.add(item)
        db.session.commit()

        return success_response(item, status_code=201)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('', methods=['GET'])
def list_items():
    """
    List all item batches with pagination and filtering
    ---
    tags:
      - Items
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: Page number
      - in: query
        name: per_page
        type: integer
        default: 20
        description: Items per page
      - in: query
        name: status
        type: string
        enum: [available, in_use, depleted]
        description: Filter by status
      - in: query
        name: item_type
        type: string
        description: Filter by item type
    responses:
      200:
        description: List of batches with pagination
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
            pagination:
              type: object
              properties:
                page:
                  type: integer
                per_page:
                  type: integer
                total_items:
                  type: integer
                total_pages:
                  type: integer
      400:
        description: Validation error
      500:
        description: Server error
    """
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Filter parameters
        status_filter = request.args.get('status')
        item_type_filter = request.args.get('item_type')

        # Build query
        query = ItemBatch.query

        if status_filter:
            query = query.filter_by(status=BatchStatus(status_filter))

        if item_type_filter:
            query = query.filter_by(item_type=item_type_filter)

        # Apply pagination
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return paginated_response(items, page, per_page, total)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<item_id>', methods=['GET'])
def get_item(item_id):
    """
    Get a specific item batch by ID
    ---
    tags:
      - Items
    parameters:
      - in: path
        name: item_id
        type: string
        required: true
        description: UUID of the item batch
    responses:
      200:
        description: Item batch details
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
        description: Item batch not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(item_id)
        item = ItemBatch.query.get(uuid_id)

        if not item:
            return error_response('NOT_FOUND', f'Item batch {item_id} not found', status_code=404)

        return success_response(item)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Update an item batch
    ---
    tags:
      - Items
    parameters:
      - in: path
        name: item_id
        type: string
        required: true
        description: UUID of the item batch
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            item_type:
              type: string
              description: Type of item
            quantity:
              type: integer
              description: Quantity in batch
            expiry_date:
              type: string
              format: date
              description: Expiry date
            status:
              type: string
              enum: [available, in_use, depleted]
              description: Batch status
    responses:
      200:
        description: Batch updated successfully
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
        description: Item batch not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(item_id)
        item = ItemBatch.query.get(uuid_id)

        if not item:
            return error_response('NOT_FOUND', f'Item batch {item_id} not found', status_code=404)

        data = request.get_json()

        # Update fields if provided
        if 'item_type' in data:
            item.item_type = data['item_type']
        if 'quantity' in data:
            item.quantity = validate_positive_integer(data['quantity'], 'quantity')
        if 'expiry_date' in data:
            item.expiry_date = datetime.fromisoformat(data['expiry_date']).date()
        if 'status' in data:
            item.status = BatchStatus(data['status'])

        item.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response(item)

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Soft delete an item batch (set status to depleted)
    ---
    tags:
      - Items
    parameters:
      - in: path
        name: item_id
        type: string
        required: true
        description: UUID of the item batch
    responses:
      200:
        description: Batch marked as depleted
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
                  example: Item batch marked as depleted
      400:
        description: Invalid UUID format
      404:
        description: Item batch not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(item_id)
        item = ItemBatch.query.get(uuid_id)

        if not item:
            return error_response('NOT_FOUND', f'Item batch {item_id} not found', status_code=404)

        # Soft delete by setting status to depleted
        item.status = BatchStatus.depleted
        item.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response({'message': 'Item batch marked as depleted'})

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/status/<status>', methods=['GET'])
def get_items_by_status(status):
    """
    Get all items filtered by status
    ---
    tags:
      - Items
    parameters:
      - in: path
        name: status
        type: string
        required: true
        enum: [available, in_use, depleted]
        description: Status to filter by
    responses:
      200:
        description: List of batches with specified status
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
        description: Invalid status value
      500:
        description: Server error
    """
    try:
        status_enum = BatchStatus(status)
        items = ItemBatch.query.filter_by(status=status_enum).all()

        return success_response(items)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', f'Invalid status: {status}', status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)
