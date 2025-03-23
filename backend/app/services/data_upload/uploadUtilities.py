from datetime import datetime
import re
from typing import List, Dict
from app.__init__ import db

from app.models import Drug, Seizure, DrugAdministration


def extract_days_from_text(text: str) -> Dict[str, str]:
    """
    Description: Extract Day information from a LTM string

    Requires:

    Modifies:

    Effects:

    @param text: Text data from docx or pdf file as a string
    @return: Returns a Dictionary mapping days name strings to the content of a day report
    """
    match = re.search(r"summary of eeg and behavior", text, re.IGNORECASE)
    if match:
        text = text[: match.start()]  # Keep only text before this match

    # Regular expression to match "Day X - " or "Day X"
    day_pattern = re.split(r"(Day\s+\d+)", text)

    parsed_days = {}
    current_day = None

    # Iterate through the split text
    for segment in day_pattern:
        segment = segment.strip()
        if re.match(r"Day\s+\d+", segment):  # Identify day headers
            current_day = segment
            parsed_days[current_day] = ""
        elif current_day:
            parsed_days[current_day] += segment + "\n"

    return parsed_days


def extract_time_for_DB(time: str) -> datetime:
    time_obj = datetime.strptime(time, "%H:%M:%S").time()
    return time_obj


def store_seizures_array(seizures: List[Dict[str, str]], p_id: int) -> bool:
    try:
        for seizure in seizures:
            dbseizure = Seizure(
                patient_id=p_id,
                day=seizure["day"],
                start_time=extract_time_for_DB(seizure["seizure_time"]),
                duration=int(seizure["duration"]),
            )
            db.session.add(dbseizure)
        db.session.commit()
        return True
    except Exception as err:
        return False


def store_drugs_array(drugs: List[Dict[str, str]], p_id: int) -> bool:
    try:
        for drug in drugs:
            db_drugentry = Drug.query.filter_by(name=drug["name"]).first()
            if db_drugentry is None:
                db_drugentry = Drug(name=drug["name"])
                db.session.add(db_drugentry)
                db.session.commit()
            db_adminentry = DrugAdministration(
                patient_id=p_id,
                drug_id=db_drugentry.id,
                day=drug["day"],
                time=extract_time_for_DB(
                    drug["time"], dosage=int(drug["mg_administered"])
                ),
            )
            db.session.add(db_adminentry)
            db.session.commit()
        return True
    except Exception as err:
        return False
