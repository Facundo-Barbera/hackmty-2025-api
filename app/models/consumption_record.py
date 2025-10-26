import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class ConsumptionRecord(db.Model):
    """Model for audit trail of inventory consumption via scanning."""
    __tablename__ = 'consumption_records'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('drawers.id'), nullable=False)
    batch_id = db.Column(UUID(as_uuid=True), db.ForeignKey('item_batches.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False)
    quantity_consumed = db.Column(db.Integer, nullable=False)
    employee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('employees.id'), nullable=False)
    job_id = db.Column(UUID(as_uuid=True), db.ForeignKey('packing_jobs.id'), nullable=True)  # Optional link to packing job
    consumed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    drawer = db.relationship('Drawer', back_populates='consumption_records')
    batch = db.relationship('ItemBatch', back_populates='consumption_records')
    product = db.relationship('Product', back_populates='consumption_records')
    employee = db.relationship('Employee')
    job = db.relationship('PackingJob', back_populates='consumption_records')

    def __repr__(self):
        return f'<ConsumptionRecord batch={self.batch_id} qty={self.quantity_consumed}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'drawer_id': str(self.drawer_id),
            'batch_id': str(self.batch_id),
            'product_id': str(self.product_id),
            'quantity_consumed': self.quantity_consumed,
            'employee_id': str(self.employee_id),
            'job_id': str(self.job_id) if self.job_id else None,
            'consumed_at': self.consumed_at.isoformat() if self.consumed_at else None
        }
