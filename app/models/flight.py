import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
import enum

class FlightStatus(enum.Enum):
    """Enum for flight status values."""
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'

class Flight(db.Model):
    """Model for flight information."""
    __tablename__ = 'flights'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_number = db.Column(db.String(20), unique=True, nullable=False, index=True)  # e.g., "LX721"
    route = db.Column(db.String(100), nullable=False)  # e.g., "ZRH-JFK"
    departure_time = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(Enum(FlightStatus), nullable=False, default=FlightStatus.pending)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    packing_jobs = db.relationship('PackingJob', back_populates='flight', lazy='dynamic')

    def __repr__(self):
        return f'<Flight {self.flight_number} - {self.route}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'flight_number': self.flight_number,
            'route': self.route,
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
