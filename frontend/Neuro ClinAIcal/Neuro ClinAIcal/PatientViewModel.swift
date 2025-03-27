//
//  PatientViewModel.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/21/25.
//

import SwiftUI

class PatientViewModel: ObservableObject {
    @Published var patients: [Patient] = []
    
    static var baseURL: String = "http://localhost:8000"
    
    func getPatientsServer() async throws {
        guard let url = URL(string: "\(Self.baseURL)/patients") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        let decodedPatients = try JSONDecoder().decode([Patient].self, from: data)
        
        await MainActor.run {
            self.patients = decodedPatients
        }
    }
    
    func createPatientServer(name: String, dob: String? = nil) async throws {
        guard let url = URL(string: "\(Self.baseURL)/patients") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Create a dictionary for the JSON body.
        // If dob is nil, you can include it as null or simply omit it if your server supports that.
        let body: [String: Any] = [
            "name": name,
            "dob": dob as Any  // if dob is nil, JSONSerialization will encode it as null.
        ]
        
        let jsonData = try JSONSerialization.data(withJSONObject: body, options: [])
        request.httpBody = jsonData
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }
    }
    
    func deletePatientServer(patientId: Int) async throws {
        guard let url = URL(string: "\(Self.baseURL)/patients/\(patientId)") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        switch httpResponse.statusCode {
        case 204:
            print("Patient deleted successfully")
        case 404:
            print("Patient not found")
            throw URLError(.fileDoesNotExist) // Customize this error as needed.
        default:
            print("Server error: \(httpResponse.statusCode)")
            throw URLError(.badServerResponse)
        }
    }
    
    func fetchFirstReportID(forPatientId patientId: Int) async throws -> Int {
        guard let url = URL(string: "\(Self.baseURL)/patients/\(patientId)/reports") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        // Parse the JSON using JSONSerialization.
        guard let jsonArray = try JSONSerialization.jsonObject(with: data, options: []) as? [[String: Any]] else {
            throw URLError(.cannotParseResponse)
        }
        
        // Extract report_id from each dictionary.
        let reportIDs = jsonArray.compactMap { $0["report_id"] as? Int }
        
        // Return only the first report id.
        guard let firstReportID = reportIDs.first else {
            throw URLError(.cannotParseResponse)
        }
        return firstReportID
    }
    
    func fetchReportSummary(forReportID reportId: Int) async throws -> String {
        guard let url = URL(string: "\(Self.baseURL)/reports/\(reportId)") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        // Parse the JSON into a dictionary.
        guard let jsonDict = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] else {
            throw URLError(.cannotParseResponse)
        }
        
        // Extract the summary value using its key.
        guard let summary = jsonDict["summary"] as? String else {
            throw URLError(.cannotParseResponse)
        }
        
        return summary
    }
    
//    func addPatient(_ name: String, _ ltmFileLocation: URL? = nil) {
//        let newPatient = Patient(name: name)
//        patients.append(newPatient)
//    }
    
//    func deletePatient(withId id: UUID) {
//        if let index = patients.firstIndex(where: { $0.id == id }) {
//            patients.remove(at: index)
//        }
//    }
}
