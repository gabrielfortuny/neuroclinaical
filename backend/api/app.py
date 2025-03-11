from typing import Tuple
import threading
from threading import lock
from flask import Flask, Blueprint, Response, request, jsonify
from file_upload.uploadHandlers import pdf_upload_handler, supported_file_types, upload_handler


app = Flask(__name__)

Has_run = False

@app.before_request
def setup():
    with lock:
        if Has_run:
            pass
        else:
            Has_run = True
            pass
            #Initialize DB Connection and all that



#####################################################
#                                                   #
#    Please look at this document before working!   #
#                                                   #
#          All Documentation Found Here!            #
#                                                   #
#####################################################

#Document: https://docs.google.com/document/d/17hVRN6OsZDlVqTX3Rxwr7b2JXdCCcrOceVsqp42a3eU/edit?pli=1&tab=t.0


@app.route('/user/<user_id>/userpatients', methods=["GET"])
def retrieve_all_patients() -> Tuple[Response, int]: 
    #Retrieve All Patients for some User
    #Accepts JSON: {}
    #Returns JSON: {#TODO}
    return


@app.route('/user/<user_id>/patient', methods=["POST"])
def create_patient(nickname: str) -> Tuple[Response, int]: 
    #Create New Patient For Some User
    #Accepts JSON: {"name": <nickname>}
    #Returns JSON: {#TODO}
    return

@app.route('/user/<user_id>/patient/<patient_id>', methods=["GET"])
def retrieve_patient_data() -> Tuple[Response, int]: 
    #Get All Patient Info
    #Accepts JSON: {}
    #Returns JSON: {#TODO}
    return

@app.route('/user/<user_id>/patient/<patient_id>/drugadmin', methods=["GET"])
def retrieve_patient_drugadmin() -> Tuple[Response, int]: 
    #Get Patient Drug Administration Entry IDs
    #Accepts JSON: {}
    #Returns JSON: {#TODO}
    return

@app.route('/user/<user_id>/patient/<patient_id>/seizures', methods=["GET"])
def retrieve_patient_seizures() -> Tuple[Response, int]: 
    #Get Patient Seizure IDs
    #Accepts JSON: {}
    #Returns JSON: {#TODO}
    return

@app.route('/user/<user_id>/patient/<patient_id>/reports', methods=["GET"])
def retrieve_patient_reports() -> Tuple[Response, int]: 
    #Get Patient LTM Report IDs
    #Accepts JSON: {}
    #Returns JSON: {#TODO}
    return

@app.route('/user/<user_id>/patient/<patient_id>/supplemental', methods=["GET"])
def retrieve_patient_supplementary() -> Tuple[Response, int]: 
    #Get All Patient Supplemetary Report IDs
    #Accepts JSON: {}
    #Returns JSON: {#TODO}
    return

@app.route('/user/<user_id>/patient/<patient_id>', methods=["PATCH"])
def change_patient_name(nickname: str) -> Tuple[Response, int]: 
    #Change the Nickname of a Patient seen in Menu
    #Accepts JSON: {}
    #Returns JSON: {#TODO}
    return

@app.route('/user/<user_id>/patient/<patient_id>', methods=["DELETE"])
def delete_patient() -> Tuple[Response, int]: 
    #Delete a Patient from the Menu
    #Accepts JSON: {}
    #Returns JSON: {#TODO}
    return

#BELOW UNDER CONSTRUCTION
#NOTHING HERE IS FINALIZED AND POSSIBLY WILL BE COMPLETELY DELETED
@app.route('/upload', methods=['POST'])
def upload() -> str:  
    #Call Authentication here
    success = upload_handler(request.content_type, request.content_encoding)
    #TODO

    

@app.route('/testing', methods=["GET"])
def test() -> str: 
    if request.content_type in supported_file_types:
        return "OK"
    return 'Hello World!'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
