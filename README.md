# Airplane Food Trolley Management API

A Flask-based REST API for tracking and automating airplane food trolley inventory management with batch-level tracking, drawer layouts, employee management, and performance evaluation.

## Features

- **Batch-Level Tracking**: Track individual batches of items with expiry dates and quantities
- **Batch Stacking Prevention**: Critical warning system that alerts when new batches are loaded over non-depleted batches (HTTP 207 Multi-Status)
- **Drawer Management**: Organize trolleys with configurable drawer layouts
- **Employee Management**: Track employee performance with accuracy and efficiency metrics
- **Performance Evaluation**: Leaderboard and aggregated metrics for employee evaluation
- **Restock History**: Complete audit trail of all inventory actions

## Technology Stack

- **Backend**: Flask 3.0
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy with UUID primary keys
- **Migrations**: Alembic via Flask-Migrate
- **Container**: Docker + Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hackmty2025-api
```

2. Start the services:
```bash
docker-compose up --build
```

This will:
- Start PostgreSQL on port 5432
- Start Flask API on port 5000
- Create the database and run migrations automatically

3. Run database migrations (if not auto-applied):
```bash
docker-compose exec api flask db upgrade
```

4. (Optional) Seed sample data:
```bash
docker-compose exec api python scripts/seed_data.py
```

### Health Check

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "airplane-trolley-api"
}
```

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Response Formats

**Success Response (200/201):**
```json
{
  "status": "success",
  "data": { }
}
```

**Error Response (400/404/500):**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

**Warning Response (207 Multi-Status) - Batch Stacking:**
```json
{
  "status": "success_with_warning",
  "data": { },
  "warning": {
    "code": "BATCH_STACKING_DETECTED",
    "message": "2 batch(es) already loaded without depletion",
    "existing_batches": [
      {
        "batch_number": "BATCH-2025-001",
        "item_type": "Coca-Cola",
        "quantity_loaded": 24,
        "load_date": "2025-10-20T10:30:00Z"
      }
    ]
  }
}
```

## API Endpoints

### Items (Batches)

**Create Item Batch**
```bash
curl -X POST http://localhost:5000/api/items \
  -H "Content-Type: application/json" \
  -d '{
    "item_type": "Coca-Cola",
    "batch_number": "BATCH-2025-001",
    "quantity": 100,
    "expiry_date": "2025-12-31"
  }'
```

**List All Items** (with pagination and filtering)
```bash
curl "http://localhost:5000/api/items?page=1&per_page=20&status=available&item_type=Coca-Cola"
```

**Get Specific Item**
```bash
curl http://localhost:5000/api/items/{id}
```

**Update Item**
```bash
curl -X PUT http://localhost:5000/api/items/{id} \
  -H "Content-Type: application/json" \
  -d '{"quantity": 75, "status": "in_use"}'
```

**Delete Item** (soft delete - sets status to depleted)
```bash
curl -X DELETE http://localhost:5000/api/items/{id}
```

**Filter by Status**
```bash
curl http://localhost:5000/api/items/status/available
```

### Drawers

**Create Drawer**
```bash
curl -X POST http://localhost:5000/api/drawers \
  -H "Content-Type: application/json" \
  -d '{
    "drawer_code": "DR-A1",
    "trolley_id": "TROLLEY-001",
    "position": 1,
    "capacity": 50,
    "drawer_type": "cold"
  }'
```

**List All Drawers**
```bash
curl http://localhost:5000/api/drawers
```

**Get/Update/Delete Drawer**
```bash
curl http://localhost:5000/api/drawers/{id}
curl -X PUT http://localhost:5000/api/drawers/{id} -H "Content-Type: application/json" -d '{...}'
curl -X DELETE http://localhost:5000/api/drawers/{id}
```

### Drawer Layouts

**Create Layout**
```bash
curl -X POST http://localhost:5000/api/drawer-layouts \
  -H "Content-Type: application/json" \
  -d '{
    "layout_name": "Standard Cold Layout",
    "drawer_id": "<drawer-uuid>",
    "item_type": "Coca-Cola",
    "designated_quantity": 24,
    "priority_order": 1
  }'
```

**Get Layouts for Specific Drawer**
```bash
curl http://localhost:5000/api/drawer-layouts/by-drawer/{drawer_id}
```

### Drawer Status (CRITICAL - Batch Stacking Detection)

**Create Drawer Status with Batch** (Triggers stacking check)
```bash
curl -X POST http://localhost:5000/api/drawer-status \
  -H "Content-Type: application/json" \
  -d '{
    "drawer_id": "<drawer-uuid>",
    "batch_id": "<batch-uuid>",
    "quantity": 24,
    "status": "partial",
    "employee_id": "<employee-uuid>"
  }'
```

If non-depleted batches exist, returns HTTP 207 with warning.

**Mark Batch as Depleted**
```bash
curl -X POST http://localhost:5000/api/drawer-status/{status_id}/deplete-batch \
  -H "Content-Type: application/json" \
  -d '{"batch_tracking_id": "<tracking-uuid>"}'
```

**Get Current Drawer Status**
```bash
curl http://localhost:5000/api/drawer-status/drawer/{drawer_id}
```

**List Batches in Drawer**
```bash
curl http://localhost:5000/api/drawer-status/{status_id}/batches
```

**List Non-Depleted Batches**
```bash
curl http://localhost:5000/api/drawer-status/{status_id}/non-depleted-batches
```

### Employees

**Create Employee**
```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP-12345",
    "first_name": "John",
    "last_name": "Doe",
    "role": "Flight Attendant"
  }'
```

**List Employees** (with status filter)
```bash
curl "http://localhost:5000/api/employees?status=active"
```

### Restock History & Performance

**Log Restock Action**
```bash
curl -X POST http://localhost:5000/api/restock-history \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "<employee-uuid>",
    "drawer_id": "<drawer-uuid>",
    "batch_id": "<batch-uuid>",
    "action_type": "restock",
    "quantity_changed": 24,
    "completion_time_seconds": 120,
    "accuracy_score": 95.5,
    "efficiency_score": 88.0,
    "notes": "Restocked drawer A1"
  }'
```

**Get Employee Performance Metrics**
```bash
curl http://localhost:5000/api/restock-history/performance/{employee_id}
```

**Get Employee Leaderboard**
```bash
curl "http://localhost:5000/api/restock-history/leaderboard?metric=accuracy_score&limit=10"
```

**Get History by Employee**
```bash
curl http://localhost:5000/api/restock-history/employee/{employee_id}
```

**Get All Batch Stacking Warnings**
```bash
curl http://localhost:5000/api/restock-history/warnings
```

## Database Schema

The system uses 8 main tables:

1. **item_batches**: Individual batch tracking
2. **drawers**: Permanent drawer definitions
3. **drawer_layouts**: Layout templates
4. **drawer_status**: Current state of drawers
5. **drawer_batch_tracking**: Batch stacking prevention (critical)
6. **employees**: Employee management
7. **restock_history**: Action audit trail with metrics

All tables use UUID primary keys and UTC timestamps.

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:postgres@db:5432/trolley_db
SECRET_KEY=your-secret-key-here
```

## Development

### Running Migrations

Create a new migration after model changes:
```bash
docker-compose exec api flask db migrate -m "Description of changes"
```

Apply migrations:
```bash
docker-compose exec api flask db upgrade
```

Rollback migration:
```bash
docker-compose exec api flask db downgrade
```

### Accessing the Database

```bash
docker-compose exec db psql -U postgres -d trolley_db
```

### Viewing Logs

```bash
docker-compose logs -f api
```

## Testing

Run the batch stacking detection tests:
```bash
docker-compose exec api pytest tests/
```

## Production Deployment Notes

Before deploying to production:

1. Change `SECRET_KEY` to a secure random value
2. Set `FLASK_ENV=production`
3. Use a production-grade WSGI server (e.g., Gunicorn)
4. Enable HTTPS
5. Configure proper database backups
6. Set up monitoring and logging
7. Review and restrict CORS settings

## License

[Add your license here]

## Support

For issues and questions, please open an issue in the repository.
