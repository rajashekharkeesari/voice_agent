from backend.models.doctor_leaves import DoctorLeaves
from backend.models.doctor_schedules import DoctorSchedules
from backend.models.doctor_slot import DoctorSlot


class DoctorAvailabilityRepository:

    def __init__(self, session):
        self.session = session

    # =========================================================
    # Schedule
    # =========================================================

    def create_schedule(
        self,
        doctor_id,
        schedule_day,
        start_time,
        end_time,
        slot_duration
    ):
        schedule = DoctorSchedules(
            doctor_id=doctor_id,
            schedule_day=schedule_day,
            start_time=start_time,
            end_time=end_time,
            slot_duration=slot_duration
        )

        self.session.add(schedule)
        self.session.commit()
        self.session.refresh(schedule)

        return schedule

    def get_doctor_schedule(self, doctor_id):
        return (
            self.session.query(DoctorSchedules)
            .filter(
                DoctorSchedules.doctor_id == doctor_id
            )
            .order_by(DoctorSchedules.id)
            .all()
        )

    def get_schedule_by_day(
        self,
        doctor_id,
        schedule_day
    ):
        return (
            self.session.query(DoctorSchedules)
            .filter(
                DoctorSchedules.doctor_id == doctor_id,
                DoctorSchedules.schedule_day == schedule_day
            )
            .first()
        )

    def update_schedule(
        self,
        schedule_id,
        schedule_day=None,
        start_time=None,
        end_time=None,
        slot_duration=None
    ):
        schedule = self.session.get(
            DoctorSchedules,
            schedule_id
        )

        if not schedule:
            return None

        fields = {
            "schedule_day": schedule_day,
            "start_time": start_time,
            "end_time": end_time,
            "slot_duration": slot_duration
        }

        for field, value in fields.items():
            if value is not None:
                setattr(schedule, field, value)

        self.session.commit()
        self.session.refresh(schedule)

        return schedule

    def delete_schedule(self, schedule_id):
        schedule = self.session.get(
            DoctorSchedules,
            schedule_id
        )

        if not schedule:
            return None

        self.session.delete(schedule)
        self.session.commit()

        return schedule

    # =========================================================
    # Doctor Leave
    # =========================================================

    def create_leave(
        self,
        doctor_id,
        start_date,
        end_date,
        reason
    ):
        leave = DoctorLeaves(
            doctor_id=doctor_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )

        self.session.add(leave)
        self.session.commit()
        self.session.refresh(leave)

        return leave

    def get_leave_by_id(self, leave_id):
        return self.session.get(
            DoctorLeaves,
            leave_id
        )

    def get_leave_by_date(
        self,
        doctor_id,
        leave_date
    ):
        return (
            self.session.query(DoctorLeaves)
            .filter(
                DoctorLeaves.doctor_id == doctor_id,
                DoctorLeaves.start_date <= leave_date,
                DoctorLeaves.end_date >= leave_date
            )
            .first()
        )

    def get_leaves_between_dates(
        self,
        doctor_id,
        start_date,
        end_date
    ):
        return (
            self.session.query(DoctorLeaves)
            .filter(
                DoctorLeaves.doctor_id == doctor_id,
                DoctorLeaves.start_date <= end_date,
                DoctorLeaves.end_date >= start_date
            )
            .order_by(DoctorLeaves.start_date)
            .all()
        )

    def get_doctor_leaves(self, doctor_id):
        return (
            self.session.query(DoctorLeaves)
            .filter(
                DoctorLeaves.doctor_id == doctor_id
            )
            .order_by(DoctorLeaves.start_date)
            .all()
        )

    def delete_leave(self, leave_id):
        leave = self.session.get(
            DoctorLeaves,
            leave_id
        )

        if not leave:
            return None

        self.session.delete(leave)
        self.session.commit()

        return leave

    # =========================================================
    # Slots
    # =========================================================

    def create_slot(
        self,
        doctor_id,
        date,
        start_time,
        end_time,
        status="available"
    ):
        slot = DoctorSlot(
            doctor_id=doctor_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )

        self.session.add(slot)
        self.session.commit()
        self.session.refresh(slot)

        return slot

    def create_slots_for_date(
        self,
        doctor_id,
        date,
        slots
    ):
        created_slots = []

        for values in slots:

            slot = DoctorSlot(
                doctor_id=doctor_id,
                date=date,
                start_time=values[0],
                end_time=values[1],
                status=(
                    values[2]
                    if len(values) > 2
                    else "available"
                )
            )

            created_slots.append(slot)

        self.session.add_all(created_slots)
        self.session.commit()

        for slot in created_slots:
            self.session.refresh(slot)

        return created_slots

    def get_available_slots(
        self,
        doctor_id,
        date
    ):
        return (
            self.session.query(DoctorSlot)
            .filter(
                DoctorSlot.doctor_id == doctor_id,
                DoctorSlot.date == date,
                DoctorSlot.status == "available"
            )
            .order_by(DoctorSlot.start_time)
            .all()
        )

    def get_slot_by_id(self, slot_id):
        return self.session.get(
            DoctorSlot,
            slot_id
        )

    def get_slots_by_doctor_and_date(
        self,
        doctor_id,
        date
    ):
        return (
            self.session.query(DoctorSlot)
            .filter(
                DoctorSlot.doctor_id == doctor_id,
                DoctorSlot.date == date
            )
            .order_by(DoctorSlot.start_time)
            .all()
        )

    def update_slot_status(
        self,
        slot_id,
        status
    ):
        slot = self.get_slot_by_id(slot_id)

        if not slot:
            return None

        slot.status = status

        self.session.commit()
        self.session.refresh(slot)

        return slot

    def book_slot(self, slot_id):
        slot = self.get_slot_by_id(slot_id)

        if not slot:
            return None

        if slot.status != "available":
            return None

        slot.status = "booked"

        self.session.commit()
        self.session.refresh(slot)

        return slot

    def release_slot(self, slot_id):
        return self.update_slot_status(
            slot_id,
            "available"
        )
