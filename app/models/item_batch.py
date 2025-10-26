import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
import enum

class BatchStatus(enum.Enum):
    """Enum for batch status values."""
    available = 'available'
    in_use = 'in_use'
    depleted = 'depleted'

class ItemBatch(db.Model):
    """Model for individual batch tracking."""
    __tablename__ = 'item_batches'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_type = db.Column(db.String(100), nullable=False)
    batch_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    received_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status = db.Column(Enum(BatchStatus), nullable=False, default=BatchStatus.available)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    batch_trackings = db.relationship('DrawerBatchTracking', back_populates='batch', lazy='dynamic')
    restock_histories = db.relationship('RestockHistory', back_populates='batch', lazy='dynamic')

    def __repr__(self):
        return f'<ItemBatch {self.batch_number}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'item_type': self.item_type,
            'batch_number': self.batch_number,
            'quantity': self.quantity,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
