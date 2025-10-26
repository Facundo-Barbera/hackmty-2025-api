"""
Evaluation service - performance metrics aggregation for employees.
"""
from sqlalchemy import func
from app import db
from app.models import RestockHistory, Employee


def calculate_employee_performance(employee_id):
    """
    Calculate aggregated performance metrics for an employee.

    Args:
        employee_id: UUID of the employee

    Returns:
        dict: Performance summary with metrics
    """
    # Get employee
    employee = Employee.query.get(employee_id)
    if not employee:
        return None

    # Aggregate metrics from restock history
    metrics = db.session.query(
        func.count(RestockHistory.id).label('total_actions'),
        func.avg(RestockHistory.accuracy_score).label('avg_accuracy'),
        func.avg(RestockHistory.efficiency_score).label('avg_efficiency'),
        func.sum(func.cast(RestockHistory.batch_warning_triggered, db.Integer)).label('warnings_triggered'),
        func.avg(RestockHistory.completion_time_seconds).label('avg_completion_time')
    ).filter(
        RestockHistory.employee_id == employee_id
    ).first()

    return {
        'employee_id': employee.employee_id,
        'employee_name': f'{employee.first_name} {employee.last_name}',
        'total_actions': metrics.total_actions or 0,
        'average_accuracy_score': float(metrics.avg_accuracy) if metrics.avg_accuracy else 0.0,
        'average_efficiency_score': float(metrics.avg_efficiency) if metrics.avg_efficiency else 0.0,
        'warnings_triggered': metrics.warnings_triggered or 0,
        'average_completion_time_seconds': float(metrics.avg_completion_time) if metrics.avg_completion_time else 0.0
    }


def get_employee_leaderboard(metric='accuracy_score', limit=10):
    """
    Get employee rankings by performance metric.

    Args:
        metric: Metric to rank by ('accuracy_score' or 'efficiency_score')
        limit: Maximum number of employees to return

    Returns:
        list: Sorted list of employee performance data
    """
    # Determine which metric to use
    if metric == 'efficiency_score':
        score_column = RestockHistory.efficiency_score
    else:
        score_column = RestockHistory.accuracy_score

    # Build leaderboard query
    leaderboard = db.session.query(
        Employee.id,
        Employee.employee_id,
        Employee.first_name,
        Employee.last_name,
        func.count(RestockHistory.id).label('total_actions'),
        func.avg(score_column).label('avg_score')
    ).join(
        RestockHistory, RestockHistory.employee_id == Employee.id
    ).filter(
        Employee.status == 'active'
    ).group_by(
        Employee.id
    ).order_by(
        func.avg(score_column).desc()
    ).limit(limit).all()

    # Format results
    results = []
    for rank, (emp_id, emp_employee_id, first_name, last_name, total, avg_score) in enumerate(leaderboard, 1):
        results.append({
            'rank': rank,
            'employee_id': emp_employee_id,
            'employee_name': f'{first_name} {last_name}',
            'total_actions': total,
            f'average_{metric}': float(avg_score) if avg_score else 0.0
        })

    return results
