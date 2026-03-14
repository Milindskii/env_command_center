"""
db/base.py
──────────
Declarative base for all SQLAlchemy ORM models.

Every model module imports `Base` from here so that a single metadata
registry is shared across the application.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Application-wide SQLAlchemy declarative base."""

    pass
