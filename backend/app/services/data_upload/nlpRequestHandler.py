import os
import urllib
import json
import traceback
from typing import List, Dict, Any
from app.services.data_upload.uploadUtilities import find_top_k_similar
from flask import current_app

# Import validation functions from the module
from app.services.data_upload.nlpValidationHandlers import (
    validate_drug,
    validate_seizure,
)

OLLAMA_URL = os.getenv("OLLAMA_HOST")  # This should be just the base URL, like http://ollama:11434
MODEL_NAME = "mymodel"

def handle_summary_request(data: str) -> str:
    """Generate a summary of the medical report."""
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": f"Give a summary of the report: {data}",
            "stream": False,
        }
        current_app.logger.info("Sending summary request to model")
        response = send_request_to_model(payload)
        return response
    except Exception as e:
        current_app.logger.error(f"Error in handle_summary_request: {str(e)}")
        return f"Error generating summary: {str(e)}"

def handle_seizure_request(data: Dict[str, str]) -> List[Dict[str, str]]:
    """Extract seizure events from the medical report."""
    seizures = []
    try:
        for day, content in data.items():
            try:
                day_int = int(day) if day.isdigit() else 1
            except ValueError:
                day_int = 1
                
            payload = {
                "model": MODEL_NAME,
                "prompt": f"Extract all seizure events from the provided medical report and return them in a JSON list. Each seizure event should include the following fields:\
                1. **start_time**: The start time of the seizure in the format `HH:MM:SS` (e.g., `06:32:06`).\
                2. **electrodes_involved**: A list of electrodes involved at seizure onset, separated by commas (e.g., `['RMH1', 'RMH2']`).\
                3. **duration**: The duration of the seizure in a human-readable format (e.g., `1 min 30 sec`).\
                Return only the JSON list and nothing else. Here is the medical report:: {content}",
                "stream": False,
            }
            current_app.logger.info(f"Sending seizure extraction request for day {day}")
            response = send_request_to_model(payload)
            
            # Try to validate, with a maximum of 3 retries
            current_app.logger.info("Validating seizure data")
            finalized_jsons = validate_seizure(day_int, response)
            retry_count = 0
            max_retries = 3
            
            while not finalized_jsons and retry_count < max_retries:
                current_app.logger.info(f"Seizure validation retry {retry_count+1}/{max_retries}")
                response = send_request_to_model(payload)
                finalized_jsons = validate_seizure(day_int, response)
                retry_count += 1
            
            # Only extend if we have valid seizures
            if finalized_jsons:
                current_app.logger.info(f"Found {len(finalized_jsons)} seizures for day {day}")
                seizures.extend(finalized_jsons)
            else:
                current_app.logger.info(f"No seizures found for day {day}")
    except Exception as e:
        current_app.logger.error(f"Error in handle_seizure_request: {str(e)}")
        current_app.logger.error(traceback.format_exc())
    
    return seizures

def handle_drugadmin_request(data: Dict[str, str]) -> List[Dict[str, str]]:
    """Extract drug administration details from the medical report."""
    drugs = []
    try:
        for day, content in data.items():
            try:
                day_int = int(day) if day.isdigit() else 1
            except ValueError:
                day_int = 1
                
            payload = {
                "model": MODEL_NAME,
                "prompt": f"Extract all drug administration details from the following medical report and return them in a JSON list. Each drug administration should include the following fields:\
                1. `name`: The name of the drug (e.g., Lamotrigine).\
                2. `mg_administered`: The amount of drug administered in milligrams (e.g., '1000').\
                3. `code`: The clinical code associated with the administration frequency (e.g., 'BID', 'QD', 'QHS', 'mg/mg').\
                Return only valid JSON and nothing else. Here is the medical report: {content}",
                "stream": False,
            }
            current_app.logger.info(f"Sending drug extraction request for day {day}")
            response = send_request_to_model(payload)
            
            # Try to validate, with a maximum of 3 retries
            current_app.logger.info("Validating drug data")
            finalized_jsons = validate_drug(day_int, response)
            retry_count = 0
            max_retries = 3
            
            while not finalized_jsons and retry_count < max_retries:
                current_app.logger.info(f"Drug validation retry {retry_count+1}/{max_retries}")
                response = send_request_to_model(payload)
                finalized_jsons = validate_drug(day_int, response)
                retry_count += 1
            
            # Only extend if we have valid drugs
            if finalized_jsons:
                current_app.logger.info(f"Found {len(finalized_jsons)} drugs for day {day}")
                drugs.extend(finalized_jsons)
            else:
                current_app.logger.info(f"No drugs found for day {day}")
    except Exception as e:
        current_app.logger.error(f"Error in handle_drugadmin_request: {str(e)}")
        current_app.logger.error(traceback.format_exc())
    
    return drugs

def handle_chat_request(text):
    question = "What does a type 3 seizure look like?"
    k = 5  # Reduced for more focused results

    # Get and display results
    top_paragraphs = find_top_k_similar(text, question, k)
    query = ""

    query = query + f"\nQuestion: '{question}'\n"
    query = query + f"Top {k} Most Relevant Answers:"
    query = query + '='*50
    for idx, result in enumerate(top_paragraphs, 1):
        query = query + f"\nMatch #{idx} (Similarity: {result['similarity']:.3f}):"
        query = query + '-'*50 
        query = query + result["paragraph"]

    payload = {
                "model": MODEL_NAME,
                "prompt": query,
                "stream": False,
            }
    
    response = send_request_to_model(payload=payload)

    return response

def send_request_to_model(payload: Dict[str, Any]) -> str:
    """Send a request to the Ollama model and return the response."""
    # FIXED: Construct the correct API endpoint URL without duplication
    api_url = f"{OLLAMA_URL}/api/generate"
    
    # Fix for OLLAMA_HOST already containing "/api/generate"
    if OLLAMA_URL.endswith("/api/generate"):
        api_url = OLLAMA_URL
    
    try:
        current_app.logger.info(f"Sending request to model API at {api_url}")
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=None) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["response"]

    except urllib.error.URLError as e:
        current_app.logger.error(f"Error connecting to model: {str(e)}")
        return ""
    except Exception as e:
        current_app.logger.error(f"Error in send_request_to_model: {str(e)}")
        return ""