import json
import re
from typing import List, Dict, Union, Any
from datetime import datetime, timedelta

def clean_drug_name(name: str) -> str:
    # Remove common dosage forms, routes, and release types
    name = name.lower()

    # Regex patterns to remove (expandable)
    patterns = [
        r'\b(?:standard|extended|delayed|immediate)\s*release\b',
        r'\b(?:xr|er|sr|dr|ir|cr)\b',
        r'\b(?:oral|tablet|capsule|solution|suspension|chewable|liquid|dose|form)\b',
        r'\b(?:tab|cap|pill|vial|ampoule|injection|syrup)\b',
        r'\b(?:mg|mcg|g|ml|units|iu)\b',
        r'\b\d+(\.\d+)?\s*(mg|mcg|g|ml|units|iu)?\b',  # e.g. 100mg, 0.5 g
        r'[^\w\s]',  # remove punctuation
        r'\s{2,}',  # collapse multiple spaces
    ]

    for pattern in patterns:
        name = re.sub(pattern, '', name)

    return name.strip().title()


def interpolate_times(n, start="08:00:00", end="22:00:00"):
    start_dt = datetime.strptime(start, "%H:%M:%S")
    end_dt = datetime.strptime(end, "%H:%M:%S")
    if n == 1:
        return [start_dt.strftime("%H:%M:%S")]
    step = (end_dt - start_dt).seconds // (n - 1)
    return [(start_dt + timedelta(seconds=step * i)).strftime("%H:%M:%S") for i in range(n)]

def times_from_qxh(code):
    match = re.match(r"Q(\d+)H", code)
    if match:
        try:
            hours = int(match.group(1))
            if hours > 0:
                num_times = 24 // hours
                return [(datetime(1900,1,1,0,0,0) + timedelta(hours=i*hours)).strftime("%H:%M:%S") for i in range(num_times)]
        except:
            pass
    return []

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
    CODE_TO_TIME = {
        "QD": ["08:00:00"],
        "BID": ["08:00:00", "20:00:00"],
        "TID": ["08:00:00", "14:00:00", "20:00:00"],
        "QID": ["06:00:00", "12:00:00", "18:00:00", "00:00:00"],
        "QHS": ["22:00:00"],
        "PRN": [],
        "QAM": ["08:00:00"],
        "QPM": ["20:00:00"],
        "STAT": ["00:00:00"],
        "mg/mg": ["08:00:00", "20:00:00"],
        "AC": ["07:00:00", "12:00:00", "18:00:00"],
        "PC": ["08:00:00", "13:00:00", "19:00:00"],
        "HS": ["22:00:00"]
    }
    try:
        try:
            start_index = input_json.find('[')
            end_index = input_json.rfind(']')
            json_content = input_json[start_index:end_index + 1]
            data = json.loads(json_content)
        except:
            return json.dumps([], indent=2)

        updated_data = []

        for drug in data:
            try:
                drug_name = drug.get("name", "").lower()
                drug_name = clean_drug_name(drug_name)
                doses = drug.get("dose_mg", [])
                times = drug.get("time_of_administration", "n/a")
                freq_code = drug.get("frequency_code", "n/a").upper()

                # Normalize dose list
                if isinstance(doses, (int, float)) or doses == "n/a":
                    doses = [doses]
                if not isinstance(doses, list):
                    doses = []

                # Determine time list
                if isinstance(times, list):
                    # If times and doses match 1-to-1
                    if len(times) == len(doses):
                        time_list = times
                    # If dose is scalar, repeat it to match time length
                    elif len(doses) == 1:
                        doses = [doses[0]] * len(times)
                        time_list = times
                    else:
                        # mismatch → fall back to times as master
                        doses = [doses[0] if doses else "n/a"] * len(times)
                        time_list = times
                else:
                    # If no usable times, use code or interpolation
                    if freq_code in CODE_TO_TIME:
                        time_list = CODE_TO_TIME[freq_code]
                    elif "Q" in freq_code and "H" in freq_code:
                        time_list = times_from_qxh(freq_code)
                    else:
                        time_list = interpolate_times(len(doses))
                    # Match dose length
                    if len(time_list) < len(doses):
                        time_list += [time_list[-1]] * (len(doses) - len(time_list))
                    elif len(time_list) > len(doses):
                        doses += [doses[-1]] * (len(time_list) - len(doses))

                for dose, time in zip(doses, time_list):
                    updated_data.append({
                        "name": drug_name,
                        "time": time,
                        "day": day,
                        "mg_administered": dose if dose != "n/a" else None
                    })
            except:
                continue  # skip broken entry

            return updated_data

    except Exception as err:
        print(f"Validation error in validate_drug: {err}")
        return []  # Return empty list instead of False
