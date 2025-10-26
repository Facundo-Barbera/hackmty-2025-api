#!/usr/bin/env python3

"""Utility script to rebuild the database schema from the current models."""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app, db  # pylint: disable=wrong-import-position


def reset_database() -> None:
    """Drop all tables and recreate them within an application context."""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()


if __name__ == "__main__":
    reset_database()
