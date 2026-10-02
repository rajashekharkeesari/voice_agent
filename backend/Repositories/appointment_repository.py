from models.appointments import Appointment


class AppointmentRepository:

    def __init__(self, session):
        self.session = session

    def create(
        self,
        patient_id,
        doctor_id,
        appointment_date,
        slot_id,
        status="Scheduled"
    ):
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            slot_id=slot_id,
            status=status
        )

        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)

        return appointment

    def get_by_id(self, appointment_id):
        return self.session.get(Appointment, appointment_id)

    def get_by_patient_id(self, patient_id):
        return (
            self.session.query(Appointment)
            .filter(Appointment.patient_id == patient_id)
            .order_by(Appointment.appointment_date)
            .all()
        )

    def get_by_doctor_id(self, doctor_id):
        return (
            self.session.query(Appointment)
            .filter(Appointment.doctor_id == doctor_id)
            .order_by(Appointment.appointment_date)
            .all()
        )

    def get_by_date(self, appointment_date):
        return (
            self.session.query(Appointment)
            .filter(Appointment.appointment_date == appointment_date)
            .all()
        )

    def get_slot_appointment(
        self,
        doctor_id,
        appointment_date,
        slot_id,
        exclude_appointment_id=None
    ):
        query = (
            self.session.query(Appointment)
            .filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.slot_id == slot_id,
                Appointment.status != "Cancelled"
            )
        )

        if exclude_appointment_id is not None:
            query = query.filter(
                Appointment.id != exclude_appointment_id
            )

        return query.first()

    def update(self, appointment, **fields):

        for field, value in fields.items():
            if value is not None:
                setattr(appointment, field, value)

        self.session.commit()
        self.session.refresh(appointment)

        return appointment