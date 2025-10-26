# Claude Code Implementation Prompt: Airplane Food Trolley Management API

## Project Overview
Create a Flask-based REST API with PostgreSQL database for tracking and automating airplane food trolley inventory management. The system must handle batch-level item tracking, drawer layouts, employee management, and restock history with performance evaluation.

## Critical Requirements

### 1. Technology Stack
- **Framework**: Flask 3.x
- **Database**: PostgreSQL 15+
- **ORM**: Flask-SQLAlchemy
- **Migrations**: Flask-Migrate (Alembic)
- **Container**: Docker + Docker Compose for local development
- **Additional Libraries**: psycopg2-binary, Flask-CORS, python-dotenv

### 2. Project Structure
Create a well-organized project with the following structure:
```
airplane-trolley-api/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py (Flask app factory)
│   ├── config.py (Configuration management)
│   ├── models/ (SQLAlchemy models)
│   ├── routes/ (API endpoints)
│   ├── services/ (Business logic)
│   └── utils/ (Helper functions)
├── migrations/ (Alembic migrations)
└── tests/ (Unit tests - basic structure)
```

### 3. Database Schema Design

#### **Tables to Create:**

**item_batches** - Individual batch tracking (not just item types)
- id (UUID, Primary Key)
- item_type (VARCHAR) - e.g., "Coca-Cola"
- batch_number (VARCHAR, UNIQUE) - e.g., "BATCH-2025-001"
- quantity (INTEGER)
- expiry_date (DATE)
- received_date (TIMESTAMP)
- status (ENUM: 'available', 'in_use', 'depleted')
- created_at, updated_at (TIMESTAMP)

**drawers** - Permanent drawer definitions
- id (UUID, Primary Key)
- drawer_code (VARCHAR, UNIQUE)
- trolley_id (VARCHAR)
- position (INTEGER)
- capacity (INTEGER)
- drawer_type (VARCHAR) - e.g., "cold", "ambient"
- created_at, updated_at (TIMESTAMP)

**drawer_layouts** - Permanent layout templates
- id (UUID, Primary Key)
- layout_name (VARCHAR)
- drawer_id (Foreign Key -> drawers.id)
- item_type (VARCHAR)
- designated_quantity (INTEGER)
- priority_order (INTEGER)
- created_at, updated_at (TIMESTAMP)

**drawer_status** - Current state of each drawer
- id (UUID, Primary Key)
- drawer_id (Foreign Key -> drawers.id)
- status (ENUM: 'empty', 'partial', 'full', 'needs_restock')
- last_updated (TIMESTAMP)
- created_at (TIMESTAMP)

**drawer_batch_tracking** - Critical for batch stacking prevention
- id (UUID, Primary Key)
- drawer_status_id (Foreign Key -> drawer_status.id)
- batch_id (Foreign Key -> item_batches.id)
- quantity_loaded (INTEGER)
- load_date (TIMESTAMP)
- is_depleted (BOOLEAN, DEFAULT FALSE)
- depletion_date (TIMESTAMP, NULLABLE)
- batch_order (INTEGER) - tracks stacking order
- created_at (TIMESTAMP)

**employees** - Employee management (ID-based, no authentication)
- id (UUID, Primary Key)
- employee_id (VARCHAR, UNIQUE) - e.g., "EMP-12345"
- first_name (VARCHAR)
- last_name (VARCHAR)
- role (VARCHAR)
- status (ENUM: 'active', 'inactive')
- created_at, updated_at (TIMESTAMP)

**restock_history** - Restock actions with evaluation metrics
- id (UUID, Primary Key)
- employee_id (Foreign Key -> employees.id)
- drawer_id (Foreign Key -> drawers.id)
- batch_id (Foreign Key -> item_batches.id)
- action_type (ENUM: 'restock', 'removal', 'adjustment')
- quantity_changed (INTEGER)
- restock_timestamp (TIMESTAMP)
- completion_time_seconds (INTEGER)
- accuracy_score (DECIMAL)
- efficiency_score (DECIMAL)
- notes (TEXT, NULLABLE)
- batch_warning_triggered (BOOLEAN)
- created_at (TIMESTAMP)

### 4. Core Business Logic Requirements

#### **CRITICAL: Batch Stacking Prevention System**
This is the most important feature. When an employee registers a new drawer status with a batch:

1. **Check for existing non-depleted batches** in the same drawer
2. **If 1 or more batches exist** that are not depleted:
   - Return HTTP 207 (Multi-Status) response
   - Include warning message: "WARNING: {count} batch(es) already in drawer without depletion"
   - Provide list of existing batches with details (batch_number, quantity_loaded, load_date)
   - Log the warning in restock_history with batch_warning_triggered = TRUE
   - **Still allow the operation** (this is a warning, not a block)
3. **If no existing batches**, proceed normally with HTTP 201

**Warning Response Format:**
```json
{
  "status": "success_with_warning",
  "data": { /* newly created drawer status */ },
  "warning": {
    "code": "BATCH_STACKING_DETECTED",
    "message": "2 batch(es) already loaded without depletion",
    "existing_batches": [
      {
        "batch_number": "BATCH-2025-001",
        "quantity_loaded": 24,
        "load_date": "2025-10-20T10:30:00Z",
        "item_type": "Coca-Cola"
      }
    ]
  }
}
```

#### **Batch Depletion Tracking**
- Provide an endpoint to mark a batch as depleted
- Set is_depleted = TRUE and record depletion_date
- This removes the batch from stacking detection logic

#### **Evaluation System**
- Accept pre-calculated metrics: accuracy_score, efficiency_score
- Store metrics with each restock action in restock_history
- Provide aggregation endpoints for employee performance
- Calculate average scores, total actions, warnings triggered

### 5. API Endpoints to Implement

#### **Items (Batches) - Full CRUD**
- POST /api/items - Create new item batch
- GET /api/items - List all batches (with filtering by status, item_type)
- GET /api/items/{id} - Get specific batch
- PUT /api/items/{id} - Update batch details
- DELETE /api/items/{id} - Delete batch
- GET /api/items/status/{status} - Filter by status

#### **Drawers - Full CRUD**
- POST /api/drawers - Create drawer
- GET /api/drawers - List all drawers
- GET /api/drawers/{id} - Get specific drawer
- PUT /api/drawers/{id} - Update drawer
- DELETE /api/drawers/{id} - Delete drawer

#### **Drawer Layouts - Full CRUD**
- POST /api/drawer-layouts - Create layout
- GET /api/drawer-layouts - List all layouts
- GET /api/drawer-layouts/{id} - Get specific layout
- PUT /api/drawer-layouts/{id} - Update layout
- DELETE /api/drawer-layouts/{id} - Delete layout
- GET /api/drawers/{drawer_id}/layout - Get layout for specific drawer

#### **Drawer Status - Full CRUD with Batch Tracking**
- POST /api/drawer-status - Register new status (MUST include batch stacking check)
- GET /api/drawer-status - List all statuses
- GET /api/drawer-status/{drawer_id} - Get current status for drawer
- PUT /api/drawer-status/{id} - Update status
- DELETE /api/drawer-status/{id} - Delete status
- POST /api/drawer-status/{id}/deplete-batch - Mark batch as depleted
- GET /api/drawer-status/{id}/batches - List all batches in drawer

#### **Employees - Full CRUD**
- POST /api/employees - Create employee
- GET /api/employees - List all employees
- GET /api/employees/{id} - Get specific employee
- PUT /api/employees/{id} - Update employee
- DELETE /api/employees/{id} - Delete employee

#### **Restock History & Evaluation**
- POST /api/restock-history - Log restock action (must accept accuracy_score, efficiency_score)
- GET /api/restock-history - List all history (with pagination)
- GET /api/restock-history/{id} - Get specific record
- GET /api/restock-history/employee/{employee_id} - Get history by employee
- GET /api/employees/{id}/performance - Get aggregated performance metrics
- GET /api/employees/leaderboard - Get employee rankings by metrics
- GET /api/restock-history/warnings - Get all records where batch stacking occurred

### 6. Docker Configuration Requirements

#### **docker-compose.yml**
- PostgreSQL 15 service named "db"
- Flask API service named "api" 
- Database credentials: postgres/postgres/trolley_db
- Expose PostgreSQL on port 5432
- Expose Flask on port 5000
- Persistent volume for PostgreSQL data
- API service depends on db service
- Mount current directory for development hot-reload

#### **Dockerfile**
- Use Python 3.11-slim base image
- Set working directory to /app
- Install dependencies from requirements.txt
- Copy application code
- Run Flask development server on 0.0.0.0:5000

#### **.env.example**
- DATABASE_URL template
- FLASK_ENV
- SECRET_KEY placeholder

### 7. Implementation Phases

#### **Phase 1: Foundation**
1. Create project structure with all folders
2. Set up Docker and Docker Compose files
3. Create requirements.txt with all dependencies
4. Initialize Flask app with app factory pattern
5. Configure SQLAlchemy and database connection
6. Create .gitignore for Python/Flask projects

#### **Phase 2: Database Layer**
1. Create all SQLAlchemy models with proper relationships
2. Add UUID primary keys for all tables
3. Add ENUM types for status fields
4. Set up Flask-Migrate
5. Generate initial migration
6. Test database connection and migrations

#### **Phase 3: Business Logic**
1. Create batch_tracking.py service with stacking detection logic
2. Create evaluation.py service for performance metrics
3. Add validation utilities for input data
4. Add error handling utilities

#### **Phase 4: API Endpoints**
1. Implement all Items CRUD endpoints with filtering
2. Implement all Drawers CRUD endpoints
3. Implement all Drawer Layouts CRUD endpoints
4. Implement all Drawer Status CRUD endpoints with batch tracking
5. Implement batch depletion endpoint
6. Implement all Employees CRUD endpoints
7. Implement all Restock History endpoints
8. Implement performance and leaderboard endpoints

#### **Phase 5: Polish**
1. Add comprehensive error handling (400, 404, 500 responses)
2. Add input validation on all POST/PUT endpoints
3. Add CORS configuration
4. Create README.md with API documentation and setup instructions
5. Create a seed script to populate sample data
6. Add basic test structure (at minimum, test batch stacking detection)

### 8. Key Implementation Details

#### **UUID Usage**
- Use UUID as primary keys for all tables (use uuid.uuid4() in Python)
- Return UUIDs as strings in API responses

#### **Timestamp Handling**
- Use UTC timestamps for all datetime fields
- Return ISO 8601 formatted timestamps in API responses

#### **Error Response Format**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

#### **Success Response Format**
```json
{
  "status": "success",
  "data": { /* resource data */ }
}
```

#### **Pagination for List Endpoints**
- Use query parameters: ?page=1&per_page=20
- Return pagination metadata in response

### 9. Testing Requirements
- At minimum, create test structure and one test for batch stacking detection
- Use pytest if implementing tests
- Test the critical batch stacking warning system thoroughly

### 10. Documentation Requirements

#### **README.md must include:**
- Project description
- Setup instructions (Docker commands)
- Database migration commands
- API endpoint documentation with example requests/responses
- Sample curl commands for testing
- Environment variables explanation

### 11. Special Notes
- **No authentication system** - employees are identified by employee_id only
- **Batch tracking is critical** - this is the core feature
- **Performance metrics are pre-calculated** - API only stores them
- **Focus on data integrity** - use foreign key constraints properly
- **Make it production-ready** - proper error handling, validation, logging

## Success Criteria
1. Docker Compose successfully starts both services
2. Database migrations run without errors
3. All CRUD endpoints work correctly
4. Batch stacking detection works and returns proper warnings
5. Performance metrics are stored and retrieved correctly
6. API documentation is clear and complete
7. Sample data can be seeded for testing

## Start Implementation
Begin with Phase 1 and work through each phase systematically. Ensure each phase is complete before moving to the next. Test thoroughly at each stage, especially the batch stacking detection logic.
