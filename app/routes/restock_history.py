"""
Restock History API endpoints - includes performance evaluation.
"""
from flask import Blueprint, request
from app import db
from app.models import RestockHistory, ActionType, Employee, Drawer, ItemBatch
from app.services.evaluation import calculate_employee_performance, get_employee_leaderboard
from app.utils.responses import success_response, error_response, paginated_response
from app.utils.validators import validate_uuid, validate_required_fields, validate_numeric_range
from datetime import datetime

bp = Blueprint('restock_history', __name__, url_prefix='/api/restock-history')


@bp.route('', methods=['POST'])
def create_restock_record():
    """
    Log a new restock action with pre-calculated metrics
    ---
    tags:
      - Restock History
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - action_type
            - quantity_changed
          properties:
            employee_id:
              type: string
              description: UUID of the employee (nullable)
              example: "123e4567-e89b-12d3-a456-426614174000"
            drawer_id:
              type: string
              description: UUID of the drawer (nullable)
              example: "223e4567-e89b-12d3-a456-426614174000"
            batch_id:
              type: string
              description: UUID of the batch (nullable)
              example: "323e4567-e89b-12d3-a456-426614174000"
            action_type:
              type: string
              enum: [restock, removal, adjustment]
              description: Type of action performed
              example: "restock"
            quantity_changed:
              type: integer
              description: Quantity added/removed
              example: 24
            completion_time_seconds:
              type: integer
              description: Time taken to complete action
              example: 120
            accuracy_score:
              type: number
              format: decimal
              description: Accuracy score (0-999.99)
              example: 95.5
            efficiency_score:
              type: number
              format: decimal
              description: Efficiency score (0-999.99)
              example: 88.3
            notes:
              type: string
              description: Optional notes about the action
              example: "Restocked during evening shift"
            batch_warning_triggered:
              type: boolean
              description: Whether batch stacking warning was triggered
              example: false
    responses:
      201:
        description: Restock record created successfully
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
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        validate_required_fields(data, ['action_type', 'quantity_changed'])

        # Validate UUIDs (nullable foreign keys)
        employee_uuid = None
        if 'employee_id' in data and data['employee_id']:
            employee_uuid = validate_uuid(data['employee_id'], 'employee_id')

        drawer_uuid = None
        if 'drawer_id' in data and data['drawer_id']:
            drawer_uuid = validate_uuid(data['drawer_id'], 'drawer_id')

        batch_uuid = None
        if 'batch_id' in data and data['batch_id']:
            batch_uuid = validate_uuid(data['batch_id'], 'batch_id')

        # Validate action type
        action_type_enum = ActionType(data['action_type'])

        # Validate metrics if provided
        accuracy_score = None
        if 'accuracy_score' in data and data['accuracy_score'] is not None:
            accuracy_score = validate_numeric_range(data['accuracy_score'], 'accuracy_score', 0, 999.99)

        efficiency_score = None
        if 'efficiency_score' in data and data['efficiency_score'] is not None:
            efficiency_score = validate_numeric_range(data['efficiency_score'], 'efficiency_score', 0, 999.99)

        # Create restock record
        record = RestockHistory(
            employee_id=employee_uuid,
            drawer_id=drawer_uuid,
            batch_id=batch_uuid,
            action_type=action_type_enum,
            quantity_changed=int(data['quantity_changed']),
            restock_timestamp=datetime.utcnow(),
            completion_time_seconds=data.get('completion_time_seconds'),
            accuracy_score=accuracy_score,
            efficiency_score=efficiency_score,
            notes=data.get('notes'),
            batch_warning_triggered=data.get('batch_warning_triggered', False)
        )

        db.session.add(record)
        db.session.commit()

        return success_response(record, status_code=201)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('', methods=['GET'])
def list_restock_history():
    """
    List all restock history with pagination
    ---
    tags:
      - Restock History
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
    responses:
      200:
        description: Paginated list of restock records
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
      500:
        description: Server error
    """
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Build query
        query = RestockHistory.query.order_by(RestockHistory.restock_timestamp.desc())

        # Apply pagination
        total = query.count()
        records = query.offset((page - 1) * per_page).limit(per_page).all()

        return paginated_response(records, page, per_page, total)

    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<record_id>', methods=['GET'])
def get_restock_record(record_id):
    """
    Get a specific restock record by ID
    ---
    tags:
      - Restock History
    parameters:
      - in: path
        name: record_id
        type: string
        required: true
        description: UUID of the restock record
    responses:
      200:
        description: Restock record details
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
        description: Restock record not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(record_id)
        record = RestockHistory.query.get(uuid_id)

        if not record:
            return error_response('NOT_FOUND', f'Restock record {record_id} not found', status_code=404)

        return success_response(record)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/employee/<employee_id>', methods=['GET'])
def get_history_by_employee(employee_id):
    """
    Get restock history filtered by employee
    ---
    tags:
      - Restock History
    parameters:
      - in: path
        name: employee_id
        type: string
        required: true
        description: UUID of the employee
    responses:
      200:
        description: List of restock records for this employee
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
        description: Employee not found
      500:
        description: Server error
    """
    try:
        employee_uuid = validate_uuid(employee_id, 'employee_id')

        # Check if employee exists
        employee = Employee.query.get(employee_uuid)
        if not employee:
            return error_response('NOT_FOUND', f'Employee {employee_id} not found', status_code=404)

        # Get history
        records = RestockHistory.query.filter_by(employee_id=employee_uuid).order_by(
            RestockHistory.restock_timestamp.desc()
        ).all()

        return success_response(records)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/warnings', methods=['GET'])
def get_warning_records():
    """
    Get all restock records where batch stacking warnings were triggered
    ---
    tags:
      - Restock History
    responses:
      200:
        description: List of restock records with batch stacking warnings
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
                description: Records where batch_warning_triggered = true
      500:
        description: Server error
    """
    try:
        records = RestockHistory.query.filter_by(batch_warning_triggered=True).order_by(
            RestockHistory.restock_timestamp.desc()
        ).all()

        return success_response(records)

    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


# Performance evaluation endpoints
@bp.route('/performance/<employee_id>', methods=['GET'])
def get_employee_performance(employee_id):
    """
    Get aggregated performance metrics for an employee
    ---
    tags:
      - Restock History
    parameters:
      - in: path
        name: employee_id
        type: string
        required: true
        description: UUID of the employee
    responses:
      200:
        description: Aggregated performance metrics
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                employee_id:
                  type: string
                total_actions:
                  type: integer
                avg_accuracy_score:
                  type: number
                avg_efficiency_score:
                  type: number
                warnings_triggered:
                  type: integer
      400:
        description: Invalid UUID format
      404:
        description: Employee not found
      500:
        description: Server error
    """
    try:
        employee_uuid = validate_uuid(employee_id, 'employee_id')

        # Use evaluation service
        performance = calculate_employee_performance(employee_uuid)

        if not performance:
            return error_response('NOT_FOUND', f'Employee {employee_id} not found', status_code=404)

        return success_response(performance)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Get employee rankings by performance metrics
    ---
    tags:
      - Restock History
    parameters:
      - in: query
        name: metric
        type: string
        enum: [accuracy_score, efficiency_score]
        default: accuracy_score
        description: Metric to rank employees by
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of top employees to return
    responses:
      200:
        description: Employee leaderboard rankings
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
                properties:
                  rank:
                    type: integer
                  employee_id:
                    type: string
                  employee_name:
                    type: string
                  metric_value:
                    type: number
      400:
        description: Invalid metric parameter
      500:
        description: Server error
    """
    try:
        # Query parameters
        metric = request.args.get('metric', 'accuracy_score')
        limit = request.args.get('limit', 10, type=int)

        # Validate metric
        if metric not in ['accuracy_score', 'efficiency_score']:
            return error_response('VALIDATION_ERROR', 'Metric must be accuracy_score or efficiency_score', status_code=400)

        # Use evaluation service
        leaderboard = get_employee_leaderboard(metric=metric, limit=limit)

        return success_response(leaderboard)

    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)
