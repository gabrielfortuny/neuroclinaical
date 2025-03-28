//
//  PatientViewModel.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/21/25.
//

import SwiftUI

class PatientViewModel: ObservableObject {
    @Published var patients: [Patient] = []
    
    func addPatient(_ name: String, _ ltmFileLocation: URL? = nil) {
        let newPatient = Patient(name: name, ltmFileLocation: ltmFileLocation)
        
        guard let url = URL(string: "http://192.168.1.76:5050/patients") else {
            print("Invalid URL")
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    
        let payload: [String: Any] = [
            "name": newPatient.name,
            "ltm_file_location": newPatient.ltmFileLocation?.absoluteString ?? ""
        ]

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        } catch {
            print("Failed to encode patient data: \(error)")
            return
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error adding patient: \(error)")
                return
            }

            DispatchQueue.main.async {
                self.patients.append(newPatient)
            }
        }.resume()
    }


    
    func deletePatient(withId id: UUID) {
        guard let url = URL(string: "http://192.168.1.76:5050/patients") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"

        URLSession.shared.dataTask(with: request) { _, _, error in
            if let error = error {
                print("Delete failed: \(error)")
                return
            }

            DispatchQueue.main.async {
                self.patients.removeAll { $0.id == id }
            }
        }.resume()
    }

}
