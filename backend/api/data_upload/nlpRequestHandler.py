import urllib
import json
from typing import Dict, Any

ollama_url = "http://ollama:11434/api/generate"


def handle_summary_request(data: str) -> str:
    payload = {
        "model": "example-model",
        "prompt": f"Give a summary of the report: {data}",
        "stream": False,
    }
    response = send_request_to_model(payload)
    return response


def handle_seizure_request():
    pass


def handle_drugadmin_request():
    pass


def handle_question_request():
    pass


def send_request_to_model(content: Dict[str, Any]) -> str:
    return ""
