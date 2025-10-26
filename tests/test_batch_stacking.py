"""
Tests for batch stacking detection - the critical feature.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import ItemBatch, Drawer, DrawerStatus, DrawerStatusEnum, BatchStatus
from app.services.batch_tracking import check_batch_stacking, create_drawer_status_with_batch, mark_batch_depleted
from datetime import datetime, timedelta


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_batch_stacking_detection(app):
    """Test that batch stacking is detected correctly."""
    with app.app_context():
        # Create a drawer
        drawer = Drawer(
            drawer_code="TEST-DR-01",
            trolley_id="TEST-TROLLEY",
            position=1,
            capacity=50,
            drawer_type="cold"
        )
        db.session.add(drawer)

        # Create two batches
        batch1 = ItemBatch(
            item_type="Test Item",
            batch_number="TEST-BATCH-001",
            quantity=50,
            expiry_date=(datetime.now() + timedelta(days=30)).date(),
            status=BatchStatus.available
        )
        batch2 = ItemBatch(
            item_type="Test Item",
            batch_number="TEST-BATCH-002",
            quantity=50,
            expiry_date=(datetime.now() + timedelta(days=60)).date(),
            status=BatchStatus.available
        )
        db.session.add_all([batch1, batch2])
        db.session.commit()

        # Create first drawer status with batch1
        status1, warning1 = create_drawer_status_with_batch(
            drawer_id=drawer.id,
            batch_id=batch1.id,
            quantity=25,
            status_value=DrawerStatusEnum.partial
        )

        # First batch should not have warning
        assert warning1 is None, "First batch should not trigger warning"

        # Create second drawer status with batch2 (should trigger warning)
        status2, warning2 = create_drawer_status_with_batch(
            drawer_id=drawer.id,
            batch_id=batch2.id,
            quantity=25,
            status_value=DrawerStatusEnum.partial
        )

        # Second batch should have warning
        assert warning2 is not None, "Second batch should trigger warning"
        assert warning2['code'] == 'BATCH_STACKING_DETECTED'
        assert '1 batch(es) already loaded without depletion' in warning2['message']
        assert len(warning2['existing_batches']) == 1
        assert warning2['existing_batches'][0]['batch_number'] == 'TEST-BATCH-001'


def test_batch_depletion_clears_warning(app):
    """Test that marking batch as depleted removes it from stacking detection."""
    with app.app_context():
        # Create drawer and batches
        drawer = Drawer(
            drawer_code="TEST-DR-02",
            trolley_id="TEST-TROLLEY",
            position=2,
            capacity=50,
            drawer_type="cold"
        )
        db.session.add(drawer)

        batch1 = ItemBatch(
            item_type="Test Item",
            batch_number="TEST-BATCH-003",
            quantity=50,
            expiry_date=(datetime.now() + timedelta(days=30)).date(),
            status=BatchStatus.available
        )
        batch2 = ItemBatch(
            item_type="Test Item",
            batch_number="TEST-BATCH-004",
            quantity=50,
            expiry_date=(datetime.now() + timedelta(days=60)).date(),
            status=BatchStatus.available
        )
        db.session.add_all([batch1, batch2])
        db.session.commit()

        # Add first batch
        status1, _ = create_drawer_status_with_batch(
            drawer_id=drawer.id,
            batch_id=batch1.id,
            quantity=25,
            status_value=DrawerStatusEnum.partial
        )

        # Get the batch tracking ID
        tracking = status1.batch_trackings.first()

        # Mark first batch as depleted
        mark_batch_depleted(tracking.id)

        # Add second batch (should not trigger warning now)
        status2, warning = create_drawer_status_with_batch(
            drawer_id=drawer.id,
            batch_id=batch2.id,
            quantity=25,
            status_value=DrawerStatusEnum.partial
        )

        assert warning is None, "Warning should not trigger after first batch is depleted"


def test_check_batch_stacking_empty_drawer(app):
    """Test checking batch stacking on empty drawer."""
    with app.app_context():
        drawer = Drawer(
            drawer_code="TEST-DR-03",
            trolley_id="TEST-TROLLEY",
            position=3,
            capacity=50,
            drawer_type="cold"
        )
        db.session.add(drawer)
        db.session.commit()

        # Check stacking on empty drawer
        existing = check_batch_stacking(drawer.id)

        assert existing == [], "Empty drawer should have no existing batches"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
