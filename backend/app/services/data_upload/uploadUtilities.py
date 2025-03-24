from datetime import datetime
import re
from typing import List, Dict
from flask import current_app
from app.__init__ import db

from app.models import Drug, Seizure, DrugAdministration, Electrode


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


def extract_time_for_DB(time_str: str) -> datetime.time:
    """Convert a time string to a datetime.time object for database storage."""
    if not time_str:
        return None
    try:
        time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
        return time_obj
    except ValueError:
        current_app.logger.warning(f"Invalid time format: {time_str}")
        return None


def store_seizures_array(seizures: List[Dict], p_id: int) -> bool:
    """
    Store an array of seizure data for a patient.

    Args:
        seizures: List of seizure dictionaries
        p_id: Patient ID

    Returns:
        bool: True if successful, False otherwise
    """
    if not seizures:
        current_app.logger.info("No seizures to store")
        return True

    try:
        # Use a fresh session to avoid issues with app context
        for seizure in seizures:
            # Get required fields with default values if missing
            day = seizure.get("day", 1)

            # Handle different field names
            start_time = None
            if "start_time" in seizure:
                start_time = extract_time_for_DB(seizure["start_time"])
            elif "seizure_time" in seizure:
                start_time = extract_time_for_DB(seizure["seizure_time"])

            duration = seizure.get("duration", 0)

            # Create seizure record
            db_seizure = Seizure(
                patient_id=p_id, day=day, start_time=start_time, duration=duration
            )

            # Add and flush to get ID before adding electrodes
            db.session.add(db_seizure)
            db.session.flush()

            # Process electrodes if present
            electrodes = []
            if "electrodes_involved" in seizure and seizure["electrodes_involved"]:
                electrodes = seizure["electrodes_involved"]

            # Add each electrode
            for electrode_name in electrodes:
                # Skip empty names
                if not electrode_name:
                    continue

                # Find or create electrode
                electrode = Electrode.query.filter_by(name=electrode_name).first()
                if not electrode:
                    electrode = Electrode(name=electrode_name)
                    db.session.add(electrode)
                    db.session.flush()

                # Add the association
                db_seizure.electrodes.append(electrode)

        # Commit all changes
        db.session.commit()
        current_app.logger.info(f"Successfully stored {len(seizures)} seizures")
        return True

    except Exception as err:
        db.session.rollback()
        current_app.logger.error(f"Error storing seizures: {str(err)}")
        import traceback

        current_app.logger.error(traceback.format_exc())
        return False


def store_drugs_array(drugs: List[Dict], p_id: int) -> bool:
    """
    Store drug administration data for a patient.

    Args:
        drugs: List of drug dictionaries with name, dosage, etc.
        p_id: Patient ID

    Returns:
        bool: True if successful, False otherwise
    """
    if not drugs:
        current_app.logger.info("No drugs to store")
        return True

    try:
        stored_count = 0

        for drug in drugs:
            # Skip if missing required fields
            if "name" not in drug:
                continue

            drug_name = drug.get("name", "").lower()
            if not drug_name:
                continue

            # Get dosage with fallback
            try:
                dosage = int(drug.get("mg_administered", 0))
            except (ValueError, TypeError):
                dosage = 0

            # Get day
            day = drug.get("day", 1)

            # Find or create drug record
            db_drug = Drug.query.filter_by(name=drug_name).first()
            if not db_drug:
                db_drug = Drug(name=drug_name)
                db.session.add(db_drug)
                db.session.flush()

            # Create administration record
            admin = DrugAdministration(
                patient_id=p_id, drug_id=db_drug.id, day=day, dosage=dosage
            )

            db.session.add(admin)
            stored_count += 1

            # Commit in batches to avoid long transactions
            if stored_count % 50 == 0:
                db.session.commit()

        # Final commit for any remaining items
        db.session.commit()
        current_app.logger.info(
            f"Successfully stored {stored_count} drug administrations"
        )
        return True

    except Exception as err:
        db.session.rollback()
        current_app.logger.error(f"Error storing drugs: {str(err)}")
        import traceback

        current_app.logger.error(traceback.format_exc())
        return False
