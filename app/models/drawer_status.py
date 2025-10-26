import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
import enum

class DrawerStatusEnum(enum.Enum):
    """Enum for drawer status values."""
    empty = 'empty'
    partial = 'partial'
    full = 'full'
    needs_restock = 'needs_restock'

class DrawerStatus(db.Model):
    """Model for current state of each drawer."""
    __tablename__ = 'drawer_status'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('drawers.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(Enum(DrawerStatusEnum), nullable=False, default=DrawerStatusEnum.empty)
    last_updated = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    drawer = db.relationship('Drawer', back_populates='drawer_statuses')
    batch_trackings = db.relationship('DrawerBatchTracking', back_populates='drawer_status', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<DrawerStatus {self.id}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'drawer_id': str(self.drawer_id),
            'status': self.status.value if self.status else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
