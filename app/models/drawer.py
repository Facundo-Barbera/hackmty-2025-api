import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class Drawer(db.Model):
    """Model for permanent drawer definitions."""
    __tablename__ = 'drawers'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawer_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    trolley_id = db.Column(db.String(50), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    drawer_type = db.Column(db.String(50), nullable=False)  # e.g., 'cold', 'ambient'
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    drawer_layouts = db.relationship('DrawerLayout', back_populates='drawer', lazy='dynamic', cascade='all, delete-orphan')
    drawer_statuses = db.relationship('DrawerStatus', back_populates='drawer', lazy='dynamic', cascade='all, delete-orphan')
    restock_histories = db.relationship('RestockHistory', back_populates='drawer', lazy='dynamic')

    def __repr__(self):
        return f'<Drawer {self.drawer_code}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'drawer_code': self.drawer_code,
            'trolley_id': self.trolley_id,
            'position': self.position,
            'capacity': self.capacity,
            'drawer_type': self.drawer_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
