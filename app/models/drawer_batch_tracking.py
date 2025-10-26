import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class DrawerBatchTracking(db.Model):
    """Model for critical batch stacking prevention tracking."""
    __tablename__ = 'drawer_batch_tracking'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawer_status_id = db.Column(UUID(as_uuid=True), db.ForeignKey('drawer_status.id', ondelete='CASCADE'), nullable=False)
    batch_id = db.Column(UUID(as_uuid=True), db.ForeignKey('item_batches.id', ondelete='RESTRICT'), nullable=False)
    quantity_loaded = db.Column(db.Integer, nullable=False)
    load_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    is_depleted = db.Column(db.Boolean, nullable=False, default=False)
    depletion_date = db.Column(db.DateTime(timezone=True), nullable=True)
    batch_order = db.Column(db.Integer, nullable=False)  # Tracks stacking order
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    drawer_status = db.relationship('DrawerStatus', back_populates='batch_trackings')
    batch = db.relationship('ItemBatch', back_populates='batch_trackings')

    def __repr__(self):
        return f'<DrawerBatchTracking {self.id}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'drawer_status_id': str(self.drawer_status_id),
            'batch_id': str(self.batch_id),
            'quantity_loaded': self.quantity_loaded,
            'load_date': self.load_date.isoformat() if self.load_date else None,
            'is_depleted': self.is_depleted,
            'depletion_date': self.depletion_date.isoformat() if self.depletion_date else None,
            'batch_order': self.batch_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def get_non_depleted_batches(drawer_status_id):
        """
        Get all non-depleted batches for a drawer status.
        Used for batch stacking detection.
        """
        return DrawerBatchTracking.query.filter_by(
            drawer_status_id=drawer_status_id,
            is_depleted=False
        ).all()
