from datetime import datetime, timezone

from backend.models.call_state import CallState

# Fields the agent is allowed to update via the tool. Keeps the tool safe and
# predictable (no arbitrary column writes).
UPDATABLE_FIELDS = {
    "patient_id",
    "patient_name",
    "patient_phone_number",
    "existing_patient",
    "reason_for_call",
    "call_type",
    "doctor_name",
    "doctor_id",
    "preferred_date",
    "preferred_time",
    "slot_id",
    "appointment_id",
    "stage",
    "confirmed",
}


class CallStateService:
    """Reads/writes the per-conversation receptionist state (CallState),
    keyed by thread_id. The agent updates this as it learns things from the
    patient and as it makes decisions, so state reflects both sides."""

    def __init__(self, session):
        self.session = session

    def _get_or_create(self, thread_id: str) -> CallState:
        state = (
            self.session.query(CallState)
            .filter(CallState.thread_id == thread_id)
            .first()
        )
        if state is None:
            state = CallState(thread_id=thread_id)
            self.session.add(state)
            self.session.commit()
            self.session.refresh(state)
        return state

    def get(self, thread_id: str) -> dict:
        state = self._get_or_create(thread_id)
        return self._to_dict(state)

    def update(self, thread_id: str, **fields) -> dict:
        state = self._get_or_create(thread_id)
        for key, value in fields.items():
            if key in UPDATABLE_FIELDS and value is not None and value != "":
                setattr(state, key, value)
        state.last_updated = datetime.now(timezone.utc).isoformat()
        self.session.commit()
        self.session.refresh(state)
        return self._to_dict(state)

    @staticmethod
    def _to_dict(state: CallState) -> dict:
        return {
            "thread_id": state.thread_id,
            "patient_id": state.patient_id,
            "patient_name": state.patient_name,
            "patient_phone_number": state.patient_phone_number,
            "existing_patient": state.existing_patient,
            "reason_for_call": state.reason_for_call,
            "call_type": state.call_type,
            "doctor_name": state.doctor_name,
            "doctor_id": state.doctor_id,
            "preferred_date": state.preferred_date,
            "preferred_time": state.preferred_time,
            "slot_id": state.slot_id,
            "appointment_id": state.appointment_id,
            "stage": state.stage,
            "confirmed": state.confirmed,
            "last_updated": state.last_updated,
        }
