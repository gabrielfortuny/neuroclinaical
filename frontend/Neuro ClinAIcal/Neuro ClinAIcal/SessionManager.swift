//
//  SessionManager.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/22/25.
//

import Foundation
import Alamofire

class SessionManager: ObservableObject {
    @Published var currentUser: User? = nil
    static var baseURL: String = "http://localhost:8000"
    var users: [User] = [
        User(id: 0, username: "Demo", email: "Demo@example.com")
    ]
    
    private func authenticateUser(email: String, password: String) -> User? {
        if email == "Demo@example.com" && password == "123" {
            return users.first(where: { $0.id == 0 })
        }
        return nil
    }
    
    func logIn(email: String, password: String) {
        let user = authenticateUser(email: email, password: password)
        if let user {
            currentUser = user
        }
    }
    
    func logOut() {
        currentUser = nil
    }
    
    func getPatientsServer() async throws -> [Patient] {
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
        
        return decodedPatients
    }
    
    func createPatientServer(name: String/*, dob: String? = nil*/) async throws {
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
//            "dob": dob as Any  // if dob is nil, JSONSerialization will encode it as null.
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
    
    func fetchFirstReportID(forPatientId patientId: Int) async throws -> LTMFile? {
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
        
        let decodedLTMFiles = try JSONDecoder().decode([LTMFile].self, from: data)
        
        return decodedLTMFiles.first
    }
    
    func uploadReport(forPatientId patientId: Int, fileURL: URL) async throws {
        let fileType = fileURL.pathExtension.lowercased()
        
        let fileData = try Data(contentsOf: fileURL)
        // Base64‑encode the file data.
        let base64EncodedFile = fileData.base64EncodedString()
        
        // Use Alamofire's multipart upload.
        let responseData = try await AF.upload(multipartFormData: { mpFD in
            if let patientIdData = "\(patientId)".data(using: .utf8) {
                mpFD.append(patientIdData, withName: "patient_id")
            }
            if let fileTypeData = fileType.data(using: .utf8) {
                mpFD.append(fileTypeData, withName: "file_type")
            }
            if let fileFieldData = base64EncodedFile.data(using: .utf8) {
                mpFD.append(fileFieldData, withName: "file", fileName: fileURL.lastPathComponent)
            }
        }, to: "\(Self.baseURL)/reports", method: .post)
            .validate(statusCode: 201..<300)
            .serializingData().value
        
        print("Report uploaded successfully, response data: \(responseData)")
    }
    
    func deleteReport(reportId: Int) async throws {
        // Construct the URL for the DELETE request.
        guard let url = URL(string: "\(Self.baseURL)/reports/\(reportId)") else {
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
            print("Report deleted successfully")
        case 401:
            print("Unauthorized")
            throw URLError(.userAuthenticationRequired)
        case 404:
            print("Report not found")
            throw URLError(.fileDoesNotExist)
        default:
            print("Server error: \(httpResponse.statusCode)")
            throw URLError(.badServerResponse)
        }
    }
}
