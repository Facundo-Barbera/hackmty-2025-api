import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum, Numeric
import enum

class ActionType(enum.Enum):
    """Enum for restock action types."""
    restock = 'restock'
    removal = 'removal'
    adjustment = 'adjustment'

class RestockHistory(db.Model):
    """Model for restock actions with evaluation metrics."""
    __tablename__ = 'restock_history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('employees.id', ondelete='SET NULL'), nullable=True)
    drawer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('drawers.id', ondelete='SET NULL'), nullable=True)
    batch_id = db.Column(UUID(as_uuid=True), db.ForeignKey('item_batches.id', ondelete='SET NULL'), nullable=True)
    action_type = db.Column(Enum(ActionType), nullable=False)
    quantity_changed = db.Column(db.Integer, nullable=False)
    restock_timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completion_time_seconds = db.Column(db.Integer, nullable=True)
    accuracy_score = db.Column(Numeric(5, 2), nullable=True)  # Up to 999.99
    efficiency_score = db.Column(Numeric(5, 2), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    batch_warning_triggered = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    employee = db.relationship('Employee', back_populates='restock_histories')
    drawer = db.relationship('Drawer', back_populates='restock_histories')
    batch = db.relationship('ItemBatch', back_populates='restock_histories')

    def __repr__(self):
        return f'<RestockHistory {self.id}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'employee_id': str(self.employee_id) if self.employee_id else None,
            'drawer_id': str(self.drawer_id) if self.drawer_id else None,
            'batch_id': str(self.batch_id) if self.batch_id else None,
            'action_type': self.action_type.value if self.action_type else None,
            'quantity_changed': self.quantity_changed,
            'restock_timestamp': self.restock_timestamp.isoformat() if self.restock_timestamp else None,
            'completion_time_seconds': self.completion_time_seconds,
            'accuracy_score': float(self.accuracy_score) if self.accuracy_score else None,
            'efficiency_score': float(self.efficiency_score) if self.efficiency_score else None,
            'notes': self.notes,
            'batch_warning_triggered': self.batch_warning_triggered,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
