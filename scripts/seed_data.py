"""
Seed script to populate sample data for testing.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import (
    ItemBatch, BatchStatus,
    Drawer,
    DrawerLayout,
    Employee, EmployeeStatus,
    DrawerStatus, DrawerStatusEnum
)
from datetime import datetime, timedelta

def seed_database():
    """Seed the database with sample data."""
    app = create_app()

    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Creating sample item batches...")
        batches = [
            ItemBatch(
                item_type="Coca-Cola",
                batch_number="BATCH-2025-001",
                quantity=100,
                expiry_date=(datetime.now() + timedelta(days=180)).date(),
                status=BatchStatus.available
            ),
            ItemBatch(
                item_type="Sprite",
                batch_number="BATCH-2025-002",
                quantity=75,
                expiry_date=(datetime.now() + timedelta(days=150)).date(),
                status=BatchStatus.available
            ),
            ItemBatch(
                item_type="Water Bottle",
                batch_number="BATCH-2025-003",
                quantity=200,
                expiry_date=(datetime.now() + timedelta(days=365)).date(),
                status=BatchStatus.available
            ),
            ItemBatch(
                item_type="Coffee",
                batch_number="BATCH-2025-004",
                quantity=50,
                expiry_date=(datetime.now() + timedelta(days=90)).date(),
                status=BatchStatus.available
            ),
            ItemBatch(
                item_type="Sandwich",
                batch_number="BATCH-2025-005",
                quantity=30,
                expiry_date=(datetime.now() + timedelta(days=7)).date(),
                status=BatchStatus.available
            ),
        ]
        db.session.add_all(batches)
        db.session.commit()
        print(f"Created {len(batches)} item batches")

        print("Creating sample drawers...")
        drawers = [
            Drawer(
                drawer_code="DR-A1",
                trolley_id="TROLLEY-001",
                position=1,
                capacity=50,
                drawer_type="cold"
            ),
            Drawer(
                drawer_code="DR-A2",
                trolley_id="TROLLEY-001",
                position=2,
                capacity=50,
                drawer_type="cold"
            ),
            Drawer(
                drawer_code="DR-B1",
                trolley_id="TROLLEY-001",
                position=3,
                capacity=40,
                drawer_type="ambient"
            ),
            Drawer(
                drawer_code="DR-B2",
                trolley_id="TROLLEY-002",
                position=1,
                capacity=60,
                drawer_type="cold"
            ),
        ]
        db.session.add_all(drawers)
        db.session.commit()
        print(f"Created {len(drawers)} drawers")

        print("Creating sample drawer layouts...")
        layouts = [
            DrawerLayout(
                layout_name="Cold Beverages Layout",
                drawer_id=drawers[0].id,
                item_type="Coca-Cola",
                designated_quantity=24,
                priority_order=1
            ),
            DrawerLayout(
                layout_name="Cold Beverages Layout",
                drawer_id=drawers[0].id,
                item_type="Sprite",
                designated_quantity=24,
                priority_order=2
            ),
            DrawerLayout(
                layout_name="Water Layout",
                drawer_id=drawers[1].id,
                item_type="Water Bottle",
                designated_quantity=50,
                priority_order=1
            ),
            DrawerLayout(
                layout_name="Hot Beverages Layout",
                drawer_id=drawers[2].id,
                item_type="Coffee",
                designated_quantity=30,
                priority_order=1
            ),
            DrawerLayout(
                layout_name="Food Layout",
                drawer_id=drawers[2].id,
                item_type="Sandwich",
                designated_quantity=20,
                priority_order=2
            ),
        ]
        db.session.add_all(layouts)
        db.session.commit()
        print(f"Created {len(layouts)} drawer layouts")

        print("Creating sample employees...")
        employees = [
            Employee(
                employee_id="EMP-001",
                first_name="John",
                last_name="Doe",
                role="Senior Flight Attendant",
                status=EmployeeStatus.active
            ),
            Employee(
                employee_id="EMP-002",
                first_name="Jane",
                last_name="Smith",
                role="Flight Attendant",
                status=EmployeeStatus.active
            ),
            Employee(
                employee_id="EMP-003",
                first_name="Mike",
                last_name="Johnson",
                role="Flight Attendant",
                status=EmployeeStatus.active
            ),
            Employee(
                employee_id="EMP-004",
                first_name="Sarah",
                last_name="Williams",
                role="Ground Crew",
                status=EmployeeStatus.inactive
            ),
        ]
        db.session.add_all(employees)
        db.session.commit()
        print(f"Created {len(employees)} employees")

        print("Creating sample drawer status...")
        drawer_statuses = [
            DrawerStatus(
                drawer_id=drawers[0].id,
                status=DrawerStatusEnum.full,
                last_updated=datetime.utcnow()
            ),
            DrawerStatus(
                drawer_id=drawers[1].id,
                status=DrawerStatusEnum.partial,
                last_updated=datetime.utcnow()
            ),
            DrawerStatus(
                drawer_id=drawers[2].id,
                status=DrawerStatusEnum.empty,
                last_updated=datetime.utcnow()
            ),
        ]
        db.session.add_all(drawer_statuses)
        db.session.commit()
        print(f"Created {len(drawer_statuses)} drawer statuses")

        print("\nSample data seeded successfully!")
        print("\nSummary:")
        print(f"  - {len(batches)} Item Batches")
        print(f"  - {len(drawers)} Drawers")
        print(f"  - {len(layouts)} Drawer Layouts")
        print(f"  - {len(employees)} Employees")
        print(f"  - {len(drawer_statuses)} Drawer Statuses")
        print("\nYou can now test the API endpoints!")

if __name__ == '__main__':
    seed_database()
