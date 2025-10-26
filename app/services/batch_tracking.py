"""
Batch tracking service - implements critical batch stacking prevention logic.
"""
from datetime import datetime
from app import db
from app.models import DrawerStatus, DrawerBatchTracking, ItemBatch, RestockHistory, ActionType, BatchStatus


def check_batch_stacking(drawer_id):
    """
    Check for existing non-depleted batches in a drawer.
    Returns list of existing batches for warning purposes.

    Args:
        drawer_id: UUID of the drawer to check

    Returns:
        list: List of dictionaries containing existing batch information
    """
    # Get the current drawer status
    current_status = DrawerStatus.query.filter_by(drawer_id=drawer_id).first()

    if not current_status:
        return []

    # Get non-depleted batches
    non_depleted = DrawerBatchTracking.query.filter_by(
        drawer_status_id=current_status.id,
        is_depleted=False
    ).all()

    # Format batch information for warning
    existing_batches = []
    for tracking in non_depleted:
        batch = ItemBatch.query.get(tracking.batch_id)
        if batch:
            existing_batches.append({
                'batch_number': batch.batch_number,
                'item_type': batch.item_type,
                'quantity_loaded': tracking.quantity_loaded,
                'load_date': tracking.load_date.isoformat() if tracking.load_date else None
            })

    return existing_batches


def create_drawer_status_with_batch(drawer_id, batch_id, quantity, status_value, employee_id=None):
    """
    Create a new drawer status with batch tracking.
    Implements batch stacking detection and warning system.

    Args:
        drawer_id: UUID of the drawer
        batch_id: UUID of the batch being loaded
        quantity: Quantity being loaded
        status_value: Status enum value for the drawer
        employee_id: Optional UUID of employee performing the action

    Returns:
        tuple: (drawer_status_object, warning_dict or None)
    """
    # Check for batch stacking
    existing_batches = check_batch_stacking(drawer_id)
    warning = None

    if existing_batches:
        warning = {
            'code': 'BATCH_STACKING_DETECTED',
            'message': f'{len(existing_batches)} batch(es) already loaded without depletion',
            'existing_batches': existing_batches
        }

    # Create drawer status
    drawer_status = DrawerStatus(
        drawer_id=drawer_id,
        status=status_value,
        last_updated=datetime.utcnow()
    )
    db.session.add(drawer_status)
    db.session.flush()  # Get the ID without committing

    # Determine batch order
    existing_count = len(existing_batches)
    batch_order = existing_count + 1

    # Create batch tracking
    batch_tracking = DrawerBatchTracking(
        drawer_status_id=drawer_status.id,
        batch_id=batch_id,
        quantity_loaded=quantity,
        load_date=datetime.utcnow(),
        batch_order=batch_order,
        is_depleted=False
    )
    db.session.add(batch_tracking)

    # Log to restock history
    restock_record = RestockHistory(
        employee_id=employee_id,
        drawer_id=drawer_id,
        batch_id=batch_id,
        action_type=ActionType.restock,
        quantity_changed=quantity,
        restock_timestamp=datetime.utcnow(),
        batch_warning_triggered=bool(warning)
    )
    db.session.add(restock_record)

    # Commit all changes
    db.session.commit()

    return drawer_status, warning


def mark_batch_depleted(batch_tracking_id):
    """
    Mark a batch as depleted, removing it from stacking detection.

    Args:
        batch_tracking_id: UUID of the batch tracking record

    Returns:
        DrawerBatchTracking: Updated batch tracking object or None if not found
    """
    tracking = DrawerBatchTracking.query.get(batch_tracking_id)

    if not tracking:
        return None

    tracking.is_depleted = True
    tracking.depletion_date = datetime.utcnow()

    # Optionally update the item batch status
    batch = ItemBatch.query.get(tracking.batch_id)
    if batch and batch.quantity == tracking.quantity_loaded:
        batch.status = BatchStatus.depleted

    db.session.commit()

    return tracking
