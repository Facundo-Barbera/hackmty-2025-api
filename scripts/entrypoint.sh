#!/bin/sh
# Entrypoint script for automatic database migrations

echo "=========================================="
echo "Airplane Trolley API - Starting up..."
echo "=========================================="

echo "Waiting for PostgreSQL to be ready..."
sleep 3

echo "Resetting database schema from models..."
python /app/scripts/reset_database.py

if [ $? -eq 0 ]; then
    echo "Database reset completed successfully!"
else
    echo "ERROR: Database reset failed!"
    exit 1
fi

echo "=========================================="
echo "Starting Flask application..."
echo "=========================================="
python -m flask run --host=0.0.0.0 --port=5000
