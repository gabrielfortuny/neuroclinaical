from app.__init__ import db
from app.models import Conversation, Message, Patient
import json

def conversationHandler(patient_id: int) -> tuple[json, int]:
    db.session.get(Patient, patient_id)
    