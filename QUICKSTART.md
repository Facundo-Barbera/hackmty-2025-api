# Quick Start Guide

## Implementation Complete!

The Airplane Food Trolley Management API has been fully implemented with all features from the specification.

## What Was Built

### 1. Complete Backend Infrastructure
- Flask 3.0 REST API with 38 endpoints
- PostgreSQL 15 database with 8 tables
- Docker containerization for easy deployment
- UUID primary keys throughout
- UTC timestamps with timezone support

### 2. Database Models (8 Tables)
- `item_batches` - Individual batch tracking with expiry dates
- `drawers` - Permanent drawer definitions
- `drawer_layouts` - Layout templates
- `drawer_status` - Current state of drawers
- `drawer_batch_tracking` - Critical batch stacking prevention
- `employees` - Employee management
- `restock_history` - Complete audit trail with metrics

### 3. Critical Batch Stacking Prevention System
- Detects when new batches are loaded over non-depleted batches
- Returns HTTP 207 Multi-Status with warning details
- Logs all warnings to restock_history
- Allows batch depletion marking to clear warnings

### 4. Performance Evaluation System
- Employee performance metrics (accuracy, efficiency scores)
- Leaderboard rankings
- Aggregated statistics
- Warning tracking per employee

### 5. Complete API Endpoints (38 Total)

**Items (Batches)** - 6 endpoints
- Full CRUD operations
- Status filtering
- Pagination support

**Drawers** - 5 endpoints
- Full CRUD operations

**Drawer Layouts** - 6 endpoints
- Full CRUD operations
- Get layouts by drawer

**Drawer Status** - 8 endpoints (CRITICAL)
- Create with batch stacking detection
- Mark batches as depleted
- List batches (all / non-depleted)

**Employees** - 5 endpoints
- Full CRUD operations
- Status filtering

**Restock History** - 8 endpoints
- Log restock actions with metrics
- Employee performance metrics
- Leaderboard
- Warning history

## How to Run

### Prerequisites
- Docker and Docker Compose installed

### Start the Application

1. Navigate to project directory:
```bash
cd /Users/facundobautistabarbera/Projects/hackmty2025-api
```

2. Start Docker services:
```bash
docker-compose up --build
```

This will:
- Start PostgreSQL on port 5432
- Start Flask API on port 5000
- Auto-run database migrations

3. In a new terminal, seed sample data:
```bash
docker-compose exec api python scripts/seed_data.py
```

4. Test the API:
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

## Testing the Critical Feature

### Test Batch Stacking Detection

1. Create a drawer:
```bash
curl -X POST http://localhost:5000/api/drawers \
  -H "Content-Type: application/json" \
  -d '{
    "drawer_code": "DR-TEST-01",
    "trolley_id": "TROLLEY-TEST",
    "position": 1,
    "capacity": 50,
    "drawer_type": "cold"
  }'
```

2. Create two batches:
```bash
# Batch 1
curl -X POST http://localhost:5000/api/items \
  -H "Content-Type: application/json" \
  -d '{
    "item_type": "Test Item",
    "batch_number": "BATCH-TEST-001",
    "quantity": 100,
    "expiry_date": "2025-12-31"
  }'

# Batch 2
curl -X POST http://localhost:5000/api/items \
  -H "Content-Type: application/json" \
  -d '{
    "item_type": "Test Item",
    "batch_number": "BATCH-TEST-002",
    "quantity": 100,
    "expiry_date": "2026-01-31"
  }'
```

3. Load first batch (no warning expected):
```bash
curl -X POST http://localhost:5000/api/drawer-status \
  -H "Content-Type: application/json" \
  -d '{
    "drawer_id": "<drawer-uuid-from-step-1>",
    "batch_id": "<batch-1-uuid>",
    "quantity": 25,
    "status": "partial"
  }'
```

4. Load second batch (WARNING EXPECTED - HTTP 207):
```bash
curl -X POST http://localhost:5000/api/drawer-status \
  -H "Content-Type: application/json" \
  -d '{
    "drawer_id": "<drawer-uuid-from-step-1>",
    "batch_id": "<batch-2-uuid>",
    "quantity": 25,
    "status": "partial"
  }'
```

Expected response with WARNING:
```json
{
  "status": "success_with_warning",
  "data": { ... },
  "warning": {
    "code": "BATCH_STACKING_DETECTED",
    "message": "1 batch(es) already loaded without depletion",
    "existing_batches": [
      {
        "batch_number": "BATCH-TEST-001",
        "item_type": "Test Item",
        "quantity_loaded": 25,
        "load_date": "2025-10-25T..."
      }
    ]
  }
}
```

## Running Tests

```bash
docker-compose exec api pytest tests/ -v
```

## Project Structure

```
hackmty2025-api/
├── app/
│   ├── __init__.py           # Flask app factory with all blueprints
│   ├── config.py             # Configuration management
│   ├── models/               # 8 SQLAlchemy models
│   ├── routes/               # 6 API blueprints (38 endpoints)
│   ├── services/             # Business logic (batch tracking, evaluation)
│   └── utils/                # Validators, response formatters
├── scripts/
│   └── seed_data.py          # Sample data seeding
├── tests/
│   └── test_batch_stacking.py # Batch stacking tests
├── docker-compose.yml         # PostgreSQL + Flask services
├── Dockerfile                 # Python 3.11 container
├── requirements.txt           # Flask 3.0, SQLAlchemy, etc.
├── README.md                  # Full API documentation
└── QUICKSTART.md             # This file
```

## Success Criteria

All requirements from the specification have been met:

- [x] Flask 3.x with PostgreSQL 15+
- [x] Docker containerization
- [x] 8 database tables with proper relationships
- [x] UUID primary keys throughout
- [x] 38 API endpoints across 6 blueprints
- [x] Batch stacking detection with HTTP 207 warnings
- [x] Batch depletion tracking
- [x] Employee performance evaluation
- [x] Leaderboard functionality
- [x] Complete CRUD operations
- [x] Input validation
- [x] Error handling
- [x] Pagination support
- [x] API documentation
- [x] Seed data script
- [x] Basic tests

## Next Steps

1. Start Docker Compose
2. Seed sample data
3. Test the API endpoints
4. Review the batch stacking detection
5. Check employee performance metrics

## Support

For detailed API documentation, see README.md

For issues, check:
- Docker logs: `docker-compose logs -f api`
- Database: `docker-compose exec db psql -U postgres -d trolley_db`
