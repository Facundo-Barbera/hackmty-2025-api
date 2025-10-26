import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class DrawerInventory(db.Model):
    """Model for tracking what products should be in each drawer."""
    __tablename__ = 'drawer_inventories'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('drawers.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)  # Current quantity in drawer
    priority_order = db.Column(db.Integer, nullable=False, default=1)  # For FEFO ordering
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    drawer = db.relationship('Drawer', back_populates='drawer_inventories')
    product = db.relationship('Product', back_populates='drawer_inventories')

    def __repr__(self):
        return f'<DrawerInventory drawer={self.drawer_id} product={self.product_id} qty={self.quantity}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'drawer_id': str(self.drawer_id),
            'product_id': str(self.product_id),
            'product': self.product.to_dict() if self.product else None,
            'quantity': self.quantity,
            'priority_order': self.priority_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
