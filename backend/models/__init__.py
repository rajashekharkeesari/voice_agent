"""Importing this package registers every ORM model on Base.metadata."""

from backend.models.departments import Department
from backend.models.doctors import Doctor
from backend.models.patients import Patient
from backend.models.appointments import Appointment
from backend.models.doctor_slot import DoctorSlot
from backend.models.doctor_schedules import DoctorSchedules
from backend.models.doctor_leaves import DoctorLeaves
from backend.models.hospital_hours import HospitalHours
from backend.models.hospital_details import HospitalService
from backend.models.hospital_closures import HospitalClosures
from backend.models.call_state import CallState

__all__ = [
    "Department",
    "Doctor",
    "Patient",
    "Appointment",
    "DoctorSlot",
    "DoctorSchedules",
    "DoctorLeaves",
    "HospitalHours",
    "HospitalService",
    "HospitalClosures",
    "CallState",
]
