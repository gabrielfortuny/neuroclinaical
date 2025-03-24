import json
import re
from typing import List, Dict, Union, Any


def extract_json_content(text):
    """Extract JSON content from text, finding the outermost array."""
    start = text.find("[")  # Find the index of the first '['
    end = text.rfind("]")  # Find the index of the last ']'

    # Extract the JSON content between the first '[' and the last ']'
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in the text.")
    return text[start : end + 1]


# Function to convert duration to seconds
def convert_duration_to_seconds(duration_str):
    """Convert duration string (e.g., '2 min 30 sec') to seconds."""
    # Extract minutes and seconds using regex
    minutes_match = re.search(
        r"(\d+)\s*(?:min|mins|minute|minutes)", duration_str, re.IGNORECASE
    )
    seconds_match = re.search(
        r"(\d+)\s*(?:sec|secs|second|seconds)", duration_str, re.IGNORECASE
    )

    minutes = int(minutes_match.group(1)) if minutes_match else 0
    seconds = int(seconds_match.group(1)) if seconds_match else 0

    return minutes * 60 + seconds


# Function to split electrode ranges into individual electrodes
def split_electrodes(electrode_str):
    """Split electrode ranges (e.g., 'RPH1-4') into individual electrodes."""
    electrodes = []
    for part in electrode_str.upper().split():
        if "-" in part:
            # Extract prefix (e.g., "RPH" from "RPH1-4")
            prefix = re.sub(r"[\d-]", "", part)  # Remove digits and hyphens
            range_part = part[len(prefix) :]  # Extract the range part (e.g., "1-4")

            # Validate the range part
            if not re.match(r"^\d+-\d+$", range_part):
                raise ValueError(f"Invalid electrode range format: {part}")

            # Split range into start and end
            start, end = map(int, range_part.split("-"))

            # Generate individual electrodes
            for i in range(start, end + 1):
                electrodes.append(f"{prefix}{i}")
        else:
            electrodes.append(part)
    return electrodes


def validate_seizure(day: int, json_text: str) -> List[Dict[str, Any]]:
    """
    Validate and process seizure data from JSON response.

    Args:
        day: The day number
        json_text: JSON string from model response

    Returns:
        List of processed seizure dictionaries or empty list on error
    """
    try:
        json_data = extract_json_content(json_text)
        data = json.loads(json_data)
        seizure_list = []

        # Process each seizure entry
        for seizure in data:
            try:
                # Check required fields
                if not all(
                    field in seizure
                    for field in ["start_time", "electrodes_involved", "duration"]
                ):
                    # Try to normalize field names
                    if "seizure_time" in seizure:
                        seizure["start_time"] = seizure.pop("seizure_time")
                    if "seizure_onset_electrodes" in seizure:
                        seizure["electrodes_involved"] = seizure.pop(
                            "seizure_onset_electrodes"
                        )

                # If still missing required fields, skip this seizure
                if not all(
                    field in seizure
                    for field in ["start_time", "electrodes_involved", "duration"]
                ):
                    continue

                # Process electrodes
                if isinstance(seizure["electrodes_involved"], list):
                    electrodes = []
                    for elec in seizure["electrodes_involved"]:
                        if isinstance(elec, str):
                            electrodes.extend(split_electrodes(elec))
                    seizure["electrodes_involved"] = electrodes
                elif isinstance(seizure["electrodes_involved"], str):
                    seizure["electrodes_involved"] = split_electrodes(
                        seizure["electrodes_involved"]
                    )

                # Convert duration to seconds
                if isinstance(seizure["duration"], str):
                    seizure["duration"] = convert_duration_to_seconds(
                        seizure["duration"]
                    )

                # Add the day field
                seizure["day"] = day

                seizure_list.append(seizure)
            except Exception as e:
                print(f"Error processing seizure: {e}")
                continue

        return seizure_list

    except Exception as err:
        print(f"Validation error in validate_seizure: {err}")
        return []  # Return empty list instead of False


def validate_drug(day: int, input_json: str) -> List[Dict[str, Any]]:
    """
    Validate and process drug administration data from JSON response.

    Args:
        day: The day number
        input_json: JSON string from model response

    Returns:
        List of processed drug dictionaries or empty list on error
    """
    try:
        # Define the mapping of codes to average time(s) in "hour:minute:second" format
        CODE_TO_TIME = {
            "QD": ["08:00:00"],  # Once daily (e.g., 8:00 AM)
            "BID": ["08:00:00", "20:00:00"],  # Twice daily (e.g., 8:00 AM and 8:00 PM)
            "TID": ["08:00:00", "14:00:00", "20:00:00"],  # Three times daily
            "QID": ["06:00:00", "12:00:00", "18:00:00", "00:00:00"],  # Four times daily
            "QHS": ["22:00:00"],  # Every night at bedtime (e.g., 10:00 PM)
            "PRN": None,  # As needed (no fixed interval)
            "QxH": None,  # Every x hours (requires additional parsing)
            "AC": ["07:00:00", "12:00:00", "18:00:00"],  # Before meals (example times)
            "PC": ["08:00:00", "13:00:00", "19:00:00"],  # After meals (example times)
            "HS": ["22:00:00"],  # At bedtime (e.g., 10:00 PM)
            "STAT": ["00:00:00"],  # Immediately (e.g., 12:00 AM)
            "AM": ["08:00:00"],  # Every morning (e.g., 8:00 AM)
            "QAM": ["08:00:00"],  # Every morning (e.g., 8:00 AM)
            "QPM": ["20:00:00"],  # Every evening (e.g., 8:00 PM)
            "mg/mg": [
                "08:00:00",
                "20:00:00",
            ],  # Twice a day (e.g., 8:00 AM and 8:00 PM)
        }

        # Parse the input JSON string: Extract content between the first '[' and the last ']'
        start_index = input_json.find("[")  # Find the index of the first '['
        end_index = input_json.rfind("]")  # Find the index of the last ']'

        if start_index == -1 or end_index == -1:
            return []  # Return empty list if no JSON array found

        # Extract the JSON content between the first '[' and the last ']'
        json_content = input_json[start_index : end_index + 1]

        # Load the extracted JSON content
        data = json.loads(json_content)

        # Process each drug entry
        updated_data = []
        for drug in data:
            try:
                if not all(
                    field in drug for field in ["name", "code", "mg_administered"]
                ):
                    continue

                drug_name = drug["name"].lower()
                code = drug.pop("code") if "code" in drug else "QD"
                times = CODE_TO_TIME.get(code, None)

                if times:
                    for time in times:
                        updated_data.append(
                            {
                                "name": drug_name,
                                "time": time,
                                "day": day,
                                "mg_administered": drug.get("mg_administered", "0"),
                            }
                        )
                else:
                    updated_data.append(
                        {
                            "name": drug_name,
                            "time": None,
                            "day": day,
                            "mg_administered": drug.get("mg_administered", "0"),
                        }
                    )
            except Exception as e:
                print(f"Error processing drug: {e}")
                continue

        return updated_data

    except Exception as err:
        print(f"Validation error in validate_drug: {err}")
        return []  # Return empty list instead of False
