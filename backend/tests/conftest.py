"""Shared test fixtures: an isolated in-memory SQLite DB seeded with a
department, a doctor, a patient, and some available slots.

These tests exercise the service layer directly (the same code the MCP tools
call), so they verify what an AI<->patient conversation can and cannot
accomplish without needing a live LLM or MCP server.
"""

from datetime import date, time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import backend.models  # noqa: F401 - registers all models on Base.metadata
from backend.db.connection import Base
from backend.models.appointments import Appointment  # noqa: F401
from backend.models.departments import Department
from backend.models.doctors import Doctor
from backend.models.doctor_slot import DoctorSlot
from backend.models.patients import Patient

TEST_DATE = date(2026, 10, 10)


@pytest.fixture()
def session():
    """Fresh in-memory DB with all tables, torn down after each test."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture()
def seeded(session):
    """Seed: Cardiology dept, Dr. Smith, patient Jane Doe, 2 open slots."""
    dept = Department(name="Cardiology")
    session.add(dept)
    session.commit()

    doctor = Doctor(name="Dr. Smith", department_id=dept.id)
    session.add(doctor)
    session.commit()

    patient = Patient(name="Jane Doe", age=42, phone_number="555-0101")
    session.add(patient)
    session.commit()

    slot1 = DoctorSlot(
        doctor_id=doctor.id,
        date=TEST_DATE,
        start_time=time(9, 0),
        end_time=time(9, 30),
        status="available",
    )
    slot2 = DoctorSlot(
        doctor_id=doctor.id,
        date=TEST_DATE,
        start_time=time(9, 30),
        end_time=time(10, 0),
        status="available",
    )
    session.add_all([slot1, slot2])
    session.commit()

    return {
        "dept": dept,
        "doctor": doctor,
        "patient": patient,
        "slot1": slot1,
        "slot2": slot2,
        "date": TEST_DATE,
    }
