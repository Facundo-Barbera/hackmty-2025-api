import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class Product(db.Model):
    """Model for product catalog with EAN barcode support."""
    __tablename__ = 'products'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ean = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Barcode
    name = db.Column(db.String(200), nullable=False)
    product_type = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    drawer_inventories = db.relationship('DrawerInventory', back_populates='product', lazy='dynamic')
    consumption_records = db.relationship('ConsumptionRecord', back_populates='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.ean} - {self.name}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'ean': self.ean,
            'name': self.name,
            'product_type': self.product_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
