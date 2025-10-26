"""
Drawer Layouts API endpoints.
"""
from flask import Blueprint, request
from app import db
from app.models import DrawerLayout, Drawer
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_uuid, validate_required_fields, validate_positive_integer
from datetime import datetime

bp = Blueprint('drawer_layouts', __name__, url_prefix='/api/drawer-layouts')


@bp.route('', methods=['POST'])
def create_layout():
    """
    Create a new drawer layout
    ---
    tags:
      - Drawer Layouts
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - layout_name
            - drawer_id
            - item_type
            - designated_quantity
            - priority_order
          properties:
            layout_name:
              type: string
              description: Name of the layout configuration
              example: "Standard Beverage Layout"
            drawer_id:
              type: string
              description: UUID of the drawer
              example: "123e4567-e89b-12d3-a456-426614174000"
            item_type:
              type: string
              description: Type of item designated for this drawer
              example: "Coca-Cola"
            designated_quantity:
              type: integer
              description: Expected quantity for this item type
              example: 24
            priority_order:
              type: integer
              description: Loading priority (0 = highest priority)
              example: 1
    responses:
      201:
        description: Layout created successfully
      400:
        description: Validation error
      404:
        description: Drawer not found
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        validate_required_fields(data, ['layout_name', 'drawer_id', 'item_type', 'designated_quantity', 'priority_order'])

        # Validate drawer exists
        drawer_uuid = validate_uuid(data['drawer_id'], 'drawer_id')
        drawer = Drawer.query.get(drawer_uuid)
        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {data["drawer_id"]} not found', status_code=404)

        # Create layout
        layout = DrawerLayout(
            layout_name=data['layout_name'],
            drawer_id=drawer_uuid,
            item_type=data['item_type'],
            designated_quantity=validate_positive_integer(data['designated_quantity'], 'designated_quantity'),
            priority_order=validate_positive_integer(data['priority_order'], 'priority_order', allow_zero=True)
        )

        db.session.add(layout)
        db.session.commit()

        return success_response(layout, status_code=201)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('', methods=['GET'])
def list_layouts():
    """
    List all drawer layouts
    ---
    tags:
      - Drawer Layouts
    responses:
      200:
        description: List of all drawer layouts
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
        layouts = DrawerLayout.query.all()
        return success_response(layouts)

    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<layout_id>', methods=['GET'])
def get_layout(layout_id):
    """
    Get a specific drawer layout by ID
    ---
    tags:
      - Drawer Layouts
    parameters:
      - in: path
        name: layout_id
        type: string
        required: true
        description: UUID of the drawer layout
    responses:
      200:
        description: Drawer layout details
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
        description: Drawer layout not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(layout_id)
        layout = DrawerLayout.query.get(uuid_id)

        if not layout:
            return error_response('NOT_FOUND', f'Drawer layout {layout_id} not found', status_code=404)

        return success_response(layout)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<layout_id>', methods=['PUT'])
def update_layout(layout_id):
    """
    Update a drawer layout
    ---
    tags:
      - Drawer Layouts
    parameters:
      - in: path
        name: layout_id
        type: string
        required: true
        description: UUID of the drawer layout
      - in: body
        name: body
        schema:
          type: object
          properties:
            layout_name:
              type: string
              description: Name of the layout configuration
            item_type:
              type: string
              description: Type of item designated
            designated_quantity:
              type: integer
              description: Expected quantity
            priority_order:
              type: integer
              description: Loading priority
    responses:
      200:
        description: Layout updated successfully
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
        description: Drawer layout not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(layout_id)
        layout = DrawerLayout.query.get(uuid_id)

        if not layout:
            return error_response('NOT_FOUND', f'Drawer layout {layout_id} not found', status_code=404)

        data = request.get_json()

        # Update fields if provided
        if 'layout_name' in data:
            layout.layout_name = data['layout_name']
        if 'item_type' in data:
            layout.item_type = data['item_type']
        if 'designated_quantity' in data:
            layout.designated_quantity = validate_positive_integer(data['designated_quantity'], 'designated_quantity')
        if 'priority_order' in data:
            layout.priority_order = validate_positive_integer(data['priority_order'], 'priority_order', allow_zero=True)

        layout.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response(layout)

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<layout_id>', methods=['DELETE'])
def delete_layout(layout_id):
    """
    Delete a drawer layout
    ---
    tags:
      - Drawer Layouts
    parameters:
      - in: path
        name: layout_id
        type: string
        required: true
        description: UUID of the drawer layout
    responses:
      200:
        description: Layout deleted successfully
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
                  example: Drawer layout deleted successfully
      400:
        description: Invalid UUID format
      404:
        description: Drawer layout not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(layout_id)
        layout = DrawerLayout.query.get(uuid_id)

        if not layout:
            return error_response('NOT_FOUND', f'Drawer layout {layout_id} not found', status_code=404)

        db.session.delete(layout)
        db.session.commit()

        return success_response({'message': 'Drawer layout deleted successfully'})

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


# Additional endpoint from specification
@bp.route('/by-drawer/<drawer_id>', methods=['GET'])
def get_layouts_by_drawer(drawer_id):
    """
    Get all layouts for a specific drawer
    ---
    tags:
      - Drawer Layouts
    parameters:
      - in: path
        name: drawer_id
        type: string
        required: true
        description: UUID of the drawer
    responses:
      200:
        description: List of layouts for the specified drawer
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
        description: Drawer not found
      500:
        description: Server error
    """
    try:
        drawer_uuid = validate_uuid(drawer_id, 'drawer_id')

        # Check if drawer exists
        drawer = Drawer.query.get(drawer_uuid)
        if not drawer:
            return error_response('NOT_FOUND', f'Drawer {drawer_id} not found', status_code=404)

        # Get layouts for this drawer
        layouts = DrawerLayout.query.filter_by(drawer_id=drawer_uuid).all()

        return success_response(layouts)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)
