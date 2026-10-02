class AppointmentService:

    def __init__(
        self,
        appointment_repository,
        doctor_repository,
        doctor_availability_repository
    ):
        self.appointment_repository = appointment_repository
        self.doctor_repository = doctor_repository
        self.doctor_availability_repository = (
            doctor_availability_repository
        )

    # --------------------------------------------------
    # CREATE APPOINTMENT
    # --------------------------------------------------

    def create_appointment(
        self,
        patient_id,
        doctor_id,
        appointment_date,
        slot_id
    ):

        # 1. Check doctor exists
        doctor = self.doctor_repository.get_doctor_by_id(
            doctor_id
        )

        if not doctor:
            raise ValueError("Doctor not found.")

        # 2. Check doctor is on leave
        leave = self.doctor_availability_repository.get_leave_by_date(
            doctor_id=doctor_id,
            leave_date=appointment_date
        )

        if leave:
            raise ValueError(
                "Doctor is on leave on this date."
            )

        # 3. Check slot exists
        slot = self.doctor_availability_repository.get_slot_by_id(
            slot_id
        )

        if not slot:
            raise ValueError("Appointment slot not found.")

        # 4. Make sure slot belongs to this doctor
        if slot.doctor_id != doctor_id:
            raise ValueError(
                "This slot does not belong to the selected doctor."
            )

        # 5. Check slot status
        if slot.status != "available":
            raise ValueError(
                "This slot is not available."
            )

        # 6. Check duplicate appointment
        existing = self.appointment_repository.get_slot_appointment(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            slot_id=slot_id
        )

        if existing:
            raise ValueError(
                "This appointment slot is already booked."
            )

        # 7. Create appointment
        appointment = self.appointment_repository.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            slot_id=slot_id
        )

        # 8. Mark slot as booked
        self.doctor_availability_repository.update_slot_status(
            slot_id,
            "booked"
        )

        return appointment

    # --------------------------------------------------
    # GET APPOINTMENT
    # --------------------------------------------------

    def get_appointment(self, appointment_id):

        appointment = self.appointment_repository.get_by_id(
            appointment_id
        )

        if not appointment:
            raise ValueError(
                "Appointment not found."
            )

        return appointment

    # --------------------------------------------------
    # PATIENT APPOINTMENTS
    # --------------------------------------------------

    def get_patient_appointments(self, patient_id):

        return self.appointment_repository.get_by_patient_id(
            patient_id
        )

    # --------------------------------------------------
    # DOCTOR APPOINTMENTS
    # --------------------------------------------------

    def get_doctor_appointments(self, doctor_id):

        return self.appointment_repository.get_by_doctor_id(
            doctor_id
        )

    # --------------------------------------------------
    # APPOINTMENTS BY DATE
    # --------------------------------------------------

    def get_appointments_by_date(self, appointment_date):

        return self.appointment_repository.get_by_date(
            appointment_date
        )

    # --------------------------------------------------
    # CHECK SLOT
    # --------------------------------------------------

    def is_slot_available(
        self,
        doctor_id,
        appointment_date,
        slot_id
    ):

        slot = self.doctor_availability_repository.get_slot_by_id(
            slot_id
        )

        if not slot:
            return False

        if slot.doctor_id != doctor_id:
            return False

        if slot.date != appointment_date:
            return False

        if slot.status != "available":
            return False

        existing = self.appointment_repository.get_slot_appointment(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            slot_id=slot_id
        )

        return existing is None

    # --------------------------------------------------
    # CANCEL APPOINTMENT
    # --------------------------------------------------

    def cancel_appointment(self, appointment_id):

        appointment = self.appointment_repository.get_by_id(
            appointment_id
        )

        if not appointment:
            raise ValueError(
                "Appointment not found."
            )

        if appointment.status == "Cancelled":
            raise ValueError(
                "Appointment is already cancelled."
            )

        # Cancel appointment
        appointment = self.appointment_repository.update(
            appointment,
            status="Cancelled"
        )

        # Release slot
        self.doctor_availability_repository.update_slot_status(
            appointment.slot_id,
            "available"
        )

        return appointment

    # --------------------------------------------------
    # RESCHEDULE APPOINTMENT
    # --------------------------------------------------

    def reschedule_appointment(
        self,
        appointment_id,
        new_date,
        new_slot_id
    ):

        appointment = self.appointment_repository.get_by_id(
            appointment_id
        )

        if not appointment:
            raise ValueError(
                "Appointment not found."
            )

        if appointment.status == "Cancelled":
            raise ValueError(
                "Cancelled appointment cannot be rescheduled."
            )

        old_slot_id = appointment.slot_id

        # Get new slot
        new_slot = (
            self.doctor_availability_repository
            .get_slot_by_id(new_slot_id)
        )

        if not new_slot:
            raise ValueError(
                "New slot not found."
            )

        if new_slot.doctor_id != appointment.doctor_id:
            raise ValueError(
                "New slot does not belong to this doctor."
            )

        if new_slot.date != new_date:
            raise ValueError(
                "New slot does not belong to the selected date."
            )

        if new_slot.status != "available":
            raise ValueError(
                "New slot is not available."
            )

        # Check duplicate appointment
        existing = self.appointment_repository.get_slot_appointment(
            doctor_id=appointment.doctor_id,
            appointment_date=new_date,
            slot_id=new_slot_id,
            exclude_appointment_id=appointment_id
        )

        if existing:
            raise ValueError(
                "The new appointment slot is already booked."
            )

        # Update appointment
        appointment = self.appointment_repository.update(
            appointment,
            appointment_date=new_date,
            slot_id=new_slot_id
        )

        # Release old slot
        self.doctor_availability_repository.update_slot_status(
            old_slot_id,
            "available"
        )

        # Book new slot
        self.doctor_availability_repository.update_slot_status(
            new_slot_id,
            "booked"
        )

        return appointment