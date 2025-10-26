import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class PackingJob(db.Model):
    """Model for packing jobs linked to flights."""
    __tablename__ = 'packing_jobs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., "JOB-123456"
    flight_id = db.Column(UUID(as_uuid=True), db.ForeignKey('flights.id'), nullable=False)
    estimated_time_seconds = db.Column(db.Integer, nullable=False)  # μ from queuing model
    actual_time_seconds = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Boolean, nullable=False, default=False)  # False = not completed, True = completed
    locked = db.Column(db.Boolean, nullable=False, default=False)  # Prevents editing after completion
    required_drawers = db.Column(db.Integer, nullable=False)  # Number of drawers for this job
    assigned_employee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('employees.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    flight = db.relationship('Flight', back_populates='packing_jobs')
    assigned_employee = db.relationship('Employee', foreign_keys=[assigned_employee_id])
    packing_job_drawers = db.relationship('PackingJobDrawer', back_populates='packing_job', lazy='dynamic', cascade='all, delete-orphan')
    consumption_records = db.relationship('ConsumptionRecord', back_populates='job', lazy='dynamic')

    def __repr__(self):
        return f'<PackingJob {self.job_id}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'job_id': self.job_id,
            'flight_id': str(self.flight_id),
            'flight': self.flight.to_dict() if self.flight else None,
            'estimated_time_seconds': self.estimated_time_seconds,
            'actual_time_seconds': self.actual_time_seconds,
            'status': self.status,
            'locked': self.locked,
            'required_drawers': self.required_drawers,
            'assigned_employee_id': str(self.assigned_employee_id) if self.assigned_employee_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
