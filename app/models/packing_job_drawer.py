import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
import enum

class PackingJobDrawerStatus(enum.Enum):
    """Enum for packing job drawer status values."""
    pending = 'pending'
    completed = 'completed'

class PackingJobDrawer(db.Model):
    """Model for packing job and drawer association with completion tracking."""
    __tablename__ = 'packing_job_drawers'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = db.Column(UUID(as_uuid=True), db.ForeignKey('packing_jobs.id'), nullable=False)
    drawer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('drawers.id'), nullable=False)
    qr_code = db.Column(db.String(100), nullable=True)  # QR code scanned for this drawer
    status = db.Column(Enum(PackingJobDrawerStatus), nullable=False, default=PackingJobDrawerStatus.pending)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    packing_job = db.relationship('PackingJob', back_populates='packing_job_drawers')
    drawer = db.relationship('Drawer', back_populates='packing_job_drawers')

    def __repr__(self):
        return f'<PackingJobDrawer job={self.job_id} drawer={self.drawer_id}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'job_id': str(self.job_id),
            'drawer_id': str(self.drawer_id),
            'drawer': self.drawer.to_dict() if self.drawer else None,
            'qr_code': self.qr_code,
            'status': self.status.value if self.status else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
