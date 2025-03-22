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
        patients.append(newPatient)
    }
    
    func deletePatient(withId id: UUID) {
        if let index = patients.firstIndex(where: { $0.id == id }) {
            patients.remove(at: index)
        }
    }
}
