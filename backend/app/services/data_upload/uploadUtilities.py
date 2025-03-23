from datetime import datetime
import re
from typing import Dict


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
