import json
import re
from typing import List, Dict


def extract_json_content(text):
    start = text.find("[")  # Find the index of the first '['
    end = text.rfind("]")  # Find the index of the last ']'

    # Extract the JSON content between the first '[' and the last ']'
    json_content = text[start : end + 1]

    # Extract the JSON content
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in the text.")
    return text[start : end + 1]


# Function to convert duration to seconds
def convert_duration_to_seconds(duration_str):
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


def validate_seizure(json_text, day) -> List[Dict[str, str]]:
    try:
        json_data = extract_json_content(json_text)

        data = json.loads(json_data)
        correct_fields = ["seizure_onset_electrodes", "seizure_time", "duration"]

        # Process each seizure entry
        for seizure in data:
            # Check if there are more than 3 fields
            if len(seizure) > 3:
                raise ValueError("A seizure entry contains more than 3 fields.")

            # Get the first three field names and their values
            first_three_fields = list(seizure.keys())[:3]
            first_three_values = [seizure.pop(field) for field in first_three_fields]

            # Overwrite with correct field names
            for new_field, value in zip(correct_fields, first_three_values):
                seizure[new_field] = value

            # Split electrode ranges into individual electrodes
            if isinstance(seizure["seizure_onset_electrodes"], list):
                # If it's a list, flatten it into a single list of electrodes
                electrodes = []
                for elec in seizure["seizure_onset_electrodes"]:
                    electrodes.extend(split_electrodes(elec))
                seizure["seizure_onset_electrodes"] = electrodes
            else:
                # If it's a single string, just split it
                seizure["seizure_onset_electrodes"] = split_electrodes(
                    seizure["seizure_onset_electrodes"]
                )

            # Convert duration to seconds
            seizure["duration"] = convert_duration_to_seconds(seizure["duration"])

            # Add the "day" field to the seizure entry
            seizure["day"] = day

        # Print the updated JSON data
        return data

    except ValueError as err:
        return False


def validate_drug(day: int, input_json: str) -> List[Dict[str, str]]:
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
        "mg/mg": ["08:00:00", "20:00:00"],  # Twice a day (e.g., 8:00 AM and 8:00 PM)
    }

    # Parse the input JSON string: Extract content between the first '[' and the last ']'
    start_index = input_json.find("[")  # Find the index of the first '['
    end_index = input_json.rfind("]")  # Find the index of the last ']'

    # Extract the JSON content between the first '[' and the last ']'
    json_content = input_json[start_index : end_index + 1]

    # Load the extracted JSON content
    data = json.loads(json_content)

    # Process each drug entry
    updated_data = []
    for drug in data:
        drug_name = drug["name"].lower()
        code = drug.pop("code")
        times = CODE_TO_TIME.get(code, None)

        if times:
            for time in times:
                updated_data.append(
                    {
                        "name": drug_name,
                        "time": time,
                        "day": day,
                        "mg_administered": drug["mg_administered"],
                    }
                )
        else:
            updated_data.append({"name": drug_name, "time": None, "day": day})

    return updated_data
