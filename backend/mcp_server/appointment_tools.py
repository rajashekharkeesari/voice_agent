from backend.services.appointment_service import AppointmentService
from backend.db.connection import get_db


def register_appointment_tools(mcp):

    @mcp.tool()
    def get_appointment(
        appointment_id: int
    ):
        """
        Get an appointment using appointment ID.
        """

        db = get_db()

        try:
            service = AppointmentService(db)

            appointment = service.get_appointment(
                appointment_id
            )

            if not appointment:
                return {
                    "success": False,
                    "message": "Appointment not found."
                }

            return {
                "success": True,
                "appointment": {
                    "id": appointment.id,
                    "patient_id": appointment.patient_id,
                    "doctor_id": appointment.doctor_id,
                    "appointment_date": str(
                        appointment.appointment_date
                    ),
                    "slot_id": appointment.slot_id,
                    "status": appointment.status
                }
            }

        finally:
            db.close()


    @mcp.tool()
    def get_patient_appointments(
        patient_id: int
    ):
        """
        Get all appointments belonging to a patient.
        """

        db = get_db()

        try:
            service = AppointmentService(db)

            appointments = service.get_patient_appointments(
                patient_id
            )

            return {
                "success": True,
                "appointments": [
                    {
                        "id": appointment.id,
                        "patient_id": appointment.patient_id,
                        "doctor_id": appointment.doctor_id,
                        "appointment_date": str(
                            appointment.appointment_date
                        ),
                        "slot_id": appointment.slot_id,
                        "status": appointment.status
                    }
                    for appointment in appointments
                ]
            }

        finally:
            db.close()


    @mcp.tool()
    def get_doctor_appointments(
        doctor_id: int
    ):
        """
        Get all appointments for a doctor.
        """

        db = get_db()

        try:
            service = AppointmentService(db)

            appointments = service.get_doctor_appointments(
                doctor_id
            )

            return {
                "success": True,
                "appointments": [
                    {
                        "id": appointment.id,
                        "patient_id": appointment.patient_id,
                        "doctor_id": appointment.doctor_id,
                        "appointment_date": str(
                            appointment.appointment_date
                        ),
                        "slot_id": appointment.slot_id,
                        "status": appointment.status
                    }
                    for appointment in appointments
                ]
            }

        finally:
            db.close()


    @mcp.tool()
    def get_appointments_by_date(
        appointment_date: str
    ):
        """
        Get all appointments on a particular date.

        Date format:
        YYYY-MM-DD
        """

        db = get_db()

        try:
            service = AppointmentService(db)

            appointments = service.get_appointments_by_date(
                appointment_date
            )

            return {
                "success": True,
                "appointments": [
                    {
                        "id": appointment.id,
                        "patient_id": appointment.patient_id,
                        "doctor_id": appointment.doctor_id,
                        "appointment_date": str(
                            appointment.appointment_date
                        ),
                        "slot_id": appointment.slot_id,
                        "status": appointment.status
                    }
                    for appointment in appointments
                ]
            }

        finally:
            db.close()


    @mcp.tool()
    def check_slot_availability(
        doctor_id: int,
        appointment_date: str,
        slot_id: int
    ):
        """
        Check whether a particular appointment slot is available.
        """

        db = get_db()

        try:
            service = AppointmentService(db)

            available = service.is_slot_available(
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                slot_id=slot_id
            )

            return {
                "success": True,
                "available": available
            }

        finally:
            db.close()


    @mcp.tool()
    def create_appointment(
        patient_id: int,
        doctor_id: int,
        appointment_date: str,
        slot_id: int
    ):
        """
        Create a new appointment.
        """

        db = get_db()

        try:
            service = AppointmentService(db)

            appointment = service.create_appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                slot_id=slot_id
            )

            return {
                "success": True,
                "message": "Appointment created successfully.",
                "appointment": {
                    "id": appointment.id,
                    "patient_id": appointment.patient_id,
                    "doctor_id": appointment.doctor_id,
                    "appointment_date": str(
                        appointment.appointment_date
                    ),
                    "slot_id": appointment.slot_id,
                    "status": appointment.status
                }
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def cancel_appointment(
        appointment_id: int
    ):
        """
        Cancel an existing appointment.
        """

        db = get_db()

        try:
            service = AppointmentService(db)

            appointment = service.cancel_appointment(
                appointment_id
            )

            if not appointment:
                return {
                    "success": False,
                    "message": "Appointment not found."
                }

            return {
                "success": True,
                "message": "Appointment cancelled successfully.",
                "appointment_id": appointment.id,
                "status": appointment.status
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def reschedule_appointment(
        appointment_id: int,
        new_doctor_id: int,
        new_appointment_date: str,
        new_slot_id: int
    ):
        """
        Reschedule an existing appointment.
        """

        db = get_db()

        try:
            service = AppointmentService(db)

            appointment = service.reschedule_appointment(
                appointment_id=appointment_id,
                new_doctor_id=new_doctor_id,
                new_appointment_date=new_appointment_date,
                new_slot_id=new_slot_id
            )

            if not appointment:
                return {
                    "success": False,
                    "message": "Appointment not found."
                }

            return {
                "success": True,
                "message": "Appointment rescheduled successfully.",
                "appointment": {
                    "id": appointment.id,
                    "patient_id": appointment.patient_id,
                    "doctor_id": appointment.doctor_id,
                    "appointment_date": str(
                        appointment.appointment_date
                    ),
                    "slot_id": appointment.slot_id,
                    "status": appointment.status
                }
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()