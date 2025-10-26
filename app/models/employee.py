import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
import enum

class EmployeeStatus(enum.Enum):
    """Enum for employee status values."""
    active = 'active'
    inactive = 'inactive'

class Employee(db.Model):
    """Model for employee management."""
    __tablename__ = 'employees'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    status = db.Column(Enum(EmployeeStatus), nullable=False, default=EmployeeStatus.active)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    restock_histories = db.relationship('RestockHistory', back_populates='employee', lazy='dynamic')

    def __repr__(self):
        return f'<Employee {self.employee_id}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
