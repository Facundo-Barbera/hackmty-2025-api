"""
Employees API endpoints.
"""
from flask import Blueprint, request
from app import db
from app.models import Employee, EmployeeStatus
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_uuid, validate_required_fields
from datetime import datetime

bp = Blueprint('employees', __name__, url_prefix='/api/employees')


@bp.route('', methods=['POST'])
def create_employee():
    """
    Create a new employee
    ---
    tags:
      - Employees
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - employee_id
            - first_name
            - last_name
            - role
          properties:
            employee_id:
              type: string
              description: Unique employee identifier
              example: "EMP-001"
            first_name:
              type: string
              description: Employee first name
              example: "John"
            last_name:
              type: string
              description: Employee last name
              example: "Doe"
            role:
              type: string
              description: Employee role
              example: "Cabin Crew"
            status:
              type: string
              enum: [active, inactive]
              description: Employee status (defaults to active)
              example: "active"
    responses:
      201:
        description: Employee created successfully
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
        description: Duplicate employee ID
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        validate_required_fields(data, ['employee_id', 'first_name', 'last_name', 'role'])

        # Check if employee_id already exists
        existing = Employee.query.filter_by(employee_id=data['employee_id']).first()
        if existing:
            return error_response('DUPLICATE_EMPLOYEE', f'Employee ID {data["employee_id"]} already exists', status_code=409)

        # Create employee
        employee = Employee(
            employee_id=data['employee_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            status=EmployeeStatus(data.get('status', 'active'))
        )

        db.session.add(employee)
        db.session.commit()

        return success_response(employee, status_code=201)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('', methods=['GET'])
def list_employees():
    """
    List all employees with optional status filter
    ---
    tags:
      - Employees
    parameters:
      - in: query
        name: status
        type: string
        enum: [active, inactive]
        description: Filter by employee status
    responses:
      200:
        description: List of employees
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
        status_filter = request.args.get('status')

        query = Employee.query

        if status_filter:
            query = query.filter_by(status=EmployeeStatus(status_filter))

        employees = query.all()
        return success_response(employees)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<emp_id>', methods=['GET'])
def get_employee(emp_id):
    """
    Get a specific employee by ID
    ---
    tags:
      - Employees
    parameters:
      - in: path
        name: emp_id
        type: string
        required: true
        description: UUID of the employee
    responses:
      200:
        description: Employee details
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
        description: Employee not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(emp_id)
        employee = Employee.query.get(uuid_id)

        if not employee:
            return error_response('NOT_FOUND', f'Employee {emp_id} not found', status_code=404)

        return success_response(employee)

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<emp_id>', methods=['PUT'])
def update_employee(emp_id):
    """
    Update an employee
    ---
    tags:
      - Employees
    parameters:
      - in: path
        name: emp_id
        type: string
        required: true
        description: UUID of the employee
      - in: body
        name: body
        schema:
          type: object
          properties:
            first_name:
              type: string
              description: Employee first name
            last_name:
              type: string
              description: Employee last name
            role:
              type: string
              description: Employee role
            status:
              type: string
              enum: [active, inactive]
              description: Employee status
    responses:
      200:
        description: Employee updated successfully
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
        description: Employee not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(emp_id)
        employee = Employee.query.get(uuid_id)

        if not employee:
            return error_response('NOT_FOUND', f'Employee {emp_id} not found', status_code=404)

        data = request.get_json()

        # Update fields if provided
        if 'first_name' in data:
            employee.first_name = data['first_name']
        if 'last_name' in data:
            employee.last_name = data['last_name']
        if 'role' in data:
            employee.role = data['role']
        if 'status' in data:
            employee.status = EmployeeStatus(data['status'])

        employee.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response(employee)

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)


@bp.route('/<emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    """
    Soft delete an employee (set status to inactive)
    ---
    tags:
      - Employees
    parameters:
      - in: path
        name: emp_id
        type: string
        required: true
        description: UUID of the employee
    responses:
      200:
        description: Employee marked as inactive
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
                  example: Employee marked as inactive
      400:
        description: Invalid UUID format
      404:
        description: Employee not found
      500:
        description: Server error
    """
    try:
        uuid_id = validate_uuid(emp_id)
        employee = Employee.query.get(uuid_id)

        if not employee:
            return error_response('NOT_FOUND', f'Employee {emp_id} not found', status_code=404)

        # Soft delete by setting status to inactive
        employee.status = EmployeeStatus.inactive
        employee.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response({'message': 'Employee marked as inactive'})

    except ValueError as e:
        db.session.rollback()
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
    except Exception as e:
        db.session.rollback()
        return error_response('SERVER_ERROR', str(e), status_code=500)
