from datetime import datetime
import re
from typing import List, Dict
from flask import current_app
from app import db

from app.models import Seizure, DrugAdministration, Electrode

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def split_paragraphs(text):
    """Split text into meaningful paragraphs using double newlines as separators."""
    # Split by double newlines, then clean each paragraph
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    # Further split any remaining long paragraphs that might have been concatenated
    refined_paragraphs = []
    for p in paragraphs:
        # Split if there's a pattern like "Type X:" followed by newline
        if re.search(r'Type \d+:\s*\n', p):
            sub_paragraphs = re.split(r'(Type \d+:)\s*\n', p)
            # Recombine the type markers with their content
            for i in range(1, len(sub_paragraphs), 2):
                refined_paragraphs.append(sub_paragraphs[i] + " " + sub_paragraphs[i+1])
        else:
            refined_paragraphs.append(p)
    return refined_paragraphs

def filter_paragraphs(paragraphs):
    """Remove low-value paragraphs."""
    filtered = []
    for p in paragraphs:
        # Skip very short paragraphs or placeholder text
        if len(p.split()) <= 3:
            continue
        # Skip repetitive headers
        if p.startswith("LONG-TERM EEG-VIDEO") or p.startswith("EPILEPSY LABORATORY"):
            continue
        filtered.append(p)
    return filtered
def chunk_paragraphs_by_word_count(paragraphs, max_words=150, overlap=0):
    """Split paragraphs into chunks of max_words with overlap."""
    chunks = []
    for paragraph in paragraphs:
        words = paragraph.split()
        if len(words) <= max_words:
            chunks.append(paragraph)
        else:
            for start in range(0, len(words), max_words - overlap):
                end = min(start + max_words, len(words))
                chunk = ' '.join(words[start:end])
                chunks.append(chunk)
    return chunks

def find_top_k_similar(text, question, k=3, model_name='all-mpnet-base-v2'):
    """Find top-k paragraphs most similar to the question."""
    current_app.logger.info("1")
    model = SentenceTransformer(model_name)
    current_app.logger.info("2")
    paragraphs = split_paragraphs(text)
    current_app.logger.info("3")
    paragraphs = filter_paragraphs(paragraphs)
    current_app.logger.info("4")
    paragraphs = chunk_paragraphs_by_word_count(paragraphs)
    current_app.logger.info("5")
    paragraphs = list(set(paragraphs))
    current_app.logger.info("6")
    # Generate embeddings
    paragraph_embeddings = model.encode(paragraphs)
    current_app.logger.info("7")
    question_embedding = model.encode([question])[0]
    current_app.logger.info("8")

    # Calculate similarities
    paragraph_embeddings = np.array(paragraph_embeddings)
    question_embedding = np.array(question_embedding).reshape(1, -1)

    similarities = cosine_similarity(question_embedding, paragraph_embeddings)[0]    
    current_app.logger.info("9")

    # Get top k indices
    top_k_indices = np.argsort(similarities)[-k:][::-1]
    current_app.logger.info("10")

    # Prepare results
    results = []
    for i in top_k_indices:
        current_app.logger.info("loopedy poop")
        results.append({
            "paragraph": paragraphs[i],
            "similarity": float(similarities[i])  # Convert numpy float to Python float
        })
        if len(results) == k:
            break

    return results

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
            current_app.logger.info("FINAL BEFORE ADDING TO DB")
            current_app.logger.info(    
            f"Seizure(patient_id={db_seizure.patient_id}, "
            f"day={db_seizure.day}, "
            f"start_time={db_seizure.start_time}, "
            f"duration={db_seizure.duration})"
            )

            # Add and flush to get ID before adding electrodes
            try:
                db.session.add(db_seizure)
                db.session.flush()
            except Exception as e:
                current_app.logger.info(f"PROP DUPLICATE {e}")

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

    try:
        stored_count = 0

        for drug in drugs:
            # Skip if missing required fields
            if "name" not in drug:
                continue

            drug_name = drug.get("name", "").lower()
            if not drug_name:
                continue

            drug_time = drug.get("time", "").lower()
            if not drug_name:
                continue


            # Get dosage with fallback
            try:
                dosage = int(drug.get("mg_administered", 0))
            except (ValueError, TypeError):
                dosage = 0

            # Get day
            day = drug.get("day", 1)

            

            # Create administration record
            admin = DrugAdministration(
                patient_id=p_id, day=day, dosage=dosage, drug_name=drug_name, time=drug_time
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
