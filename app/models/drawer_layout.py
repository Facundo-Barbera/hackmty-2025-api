import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class DrawerLayout(db.Model):
    """Model for permanent layout templates."""
    __tablename__ = 'drawer_layouts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    layout_name = db.Column(db.String(100), nullable=False)
    drawer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('drawers.id', ondelete='CASCADE'), nullable=False)
    item_type = db.Column(db.String(100), nullable=False)
    designated_quantity = db.Column(db.Integer, nullable=False)
    priority_order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    drawer = db.relationship('Drawer', back_populates='drawer_layouts')

    def __repr__(self):
        return f'<DrawerLayout {self.layout_name}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'layout_name': self.layout_name,
            'drawer_id': str(self.drawer_id),
            'item_type': self.item_type,
            'designated_quantity': self.designated_quantity,
            'priority_order': self.priority_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
