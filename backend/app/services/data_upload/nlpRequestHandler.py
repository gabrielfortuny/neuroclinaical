import os
import urllib
import json
from typing import List, Dict, Any

from app.services.data_upload.nlpValidationHandlers import (
    validate_drug,
    validate_seizure,
)

OLLAMA_URL = os.getenv("OLLAMA_HOST")
MODEL_NAME = "mymodel"

# TODO: Add Docstrings for everything


def handle_summary_request(data: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": f"Give a summary of the report: {data}",
        "stream": False,
    }
    response = send_request_to_model(payload)
    return response


def handle_seizure_request(data: Dict[str, str]) -> List[Dict[str, str]]:
    seizures = []
    for day, content in data.items():
        payload = {
            "model": MODEL_NAME,
            "prompt": f"Extract all seizure events from the provided medical report and return them in a JSON list. Each seizure event should include the following fields:\
            1. **start_time**: The start time of the seizure in the format `HH:MM:SS` (e.g., `06:32:06`).\
            2. **electrodes_involved**: A list of electrodes involved at seizure onset, separated by commas (e.g., `['RMH1', 'RMH2']`).\
            3. **duration**: The duration of the seizure in a human-readable format (e.g., `1 min 30 sec`).\
            Return only the JSON list and nothing else. Here is the medical report:: {content}",
            "stream": False,
        }
        response = send_request_to_model(payload)
        finalized_jsons = validate_seizure(day, response)
        while finalized_jsons == False:
            # TODO: Something to stop infinite loop maybe?
            response = send_request_to_model(payload)
            finalized_jsons = validate_seizure(day, response)
            finalized_jsons = True  # TODO remove this is broken
        seizures.extend(finalized_jsons)
    return seizures


def handle_drugadmin_request(data: Dict[str, str]) -> List[Dict[str, str]]:
    drugs = []
    for day, content in data.items():
        payload = {
            "model": MODEL_NAME,
            "prompt": f"Extract all drug administration details from the following medical report and return them in a JSON list. Each drug administration should include the following fields:\
            1. `name`: The name of the drug (e.g., Lamotrigine).\
            2. `mg_administered`: The amount of drug administered in milligrams (e.g., '1000').\
            3. `code`: The clinical code associated with the administration frequency (e.g., 'BID', 'QD', 'QHS', 'mg/mg').\
            **Clinical Codes and Definitions:**\
            QD (quaque die): Once daily.\
            BID (bis in die): Twice daily.\
            TID (ter in die): Three times daily.\
            QID (quater in die): Four times daily.\
            QHS (quaque hora somni): Every night at bedtime.\
            PRN (pro re nata): As needed.\
            QxH (quaque x hora): Every x hours (e.g., Q4H means every 4 hours).\
            AC (ante cibum): Before meals.\
            PC (post cibum): After meals.\
            HS (hora somni): At bedtime.\
            STAT (statim): Immediately.\
            AM (quaque ante meridiem): Every morning.\
            QAM (quaque ante meridiem): Every morning.\
            QPM (quaque post meridiem): Every evening.\
            mg/mg: Twice a day (e.g., '200mg/mg' means 200mg in the morning and 200mg in the evening).\
            If a drug was stopped, do not include it in the list. Focus only on drugs that were actively administered.\
            Here is the medical report: {content}",
            "stream": False,
        }
        response = send_request_to_model(payload)
        finalized_jsons = validate_drug(day, response)
        while finalized_jsons == False:
            # TODO: Something to stop infinite loop maybe?
            response = send_request_to_model(payload)
            finalized_jsons = validate_drug(day, response)
            finalized_jsons = True  # TODO remove this is broken
        drugs.extend(finalized_jsons)
    return drugs


def handle_question_request():
    pass


def send_request_to_model(payload: Dict[str, Any]) -> str:
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=None) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["response"]
    except urllib.error.URLError as e:
        return ""
