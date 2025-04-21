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
    //static var baseURL: String = "http://100.91.43.47:8000"
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
    
    func downloadReport(reportId: Int) async throws -> Data {
        guard let url = URL(string: "\(Self.baseURL)/reports/\(reportId)/download") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        switch httpResponse.statusCode {
        case 200:
            return data
        case 404:
            throw URLError(.fileDoesNotExist)
        default:
            throw URLError(.badServerResponse)
        }
    }
    
    func uploadReport(forPatientId patientId: Int, fileURL: URL) async throws {
        let fileType = fileURL.pathExtension.lowercased()
        let fileData = try Data(contentsOf: fileURL)

        guard let url = URL(string: "\(Self.baseURL)/reports") else {
            throw URLError(.badURL)
        }
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.timeoutInterval = 1000000
        
        let responseData = try await AF.upload(multipartFormData: { mpFD in
            mpFD.append(Data("\(patientId)".utf8), withName: "patient_id")
            mpFD.append(Data(fileType.utf8), withName: "file_type")
            mpFD.append(fileData, withName: "file", fileName: fileURL.lastPathComponent)
        }, with: urlRequest)
          .validate(statusCode: 201..<300)
          .serializingData().value

        print("Report uploaded, response:", responseData)
    }
    
    func deleteReport(reportId: Int) async throws {
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
    
    func fetchSupplementalMaterials(forPatientId patientId: Int) async throws -> [SupplementaryFile] {
        // Construct the URL.
        guard let url = URL(string: "\(Self.baseURL)/patients/\(patientId)/supplemental_materials") else {
            throw URLError(.badURL)
        }
        
        // Create the GET request and set the Accept header.
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        // Fetch the data.
        let (data, response) = try await URLSession.shared.data(for: request)
        
        // Ensure we have a valid HTTP response with status code 200.
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        // Decode the JSON into an array of SupplementalMaterial.
        let decoder = JSONDecoder()
        // Use the ISO8601 strategy if your dates follow ISO8601 format.
        decoder.dateDecodingStrategy = .iso8601
        guard let supplementalMaterials = try? decoder.decode([SupplementaryFile].self, from: data) else {
            throw URLError(.cannotParseResponse)
        }
        
        return supplementalMaterials
    }
    
    func downloadSupplementalMaterial(materialId: Int) async throws -> Data {
        guard let url = URL(string: "\(Self.baseURL)/supplemental_materials/\(materialId)/download") else {
            throw URLError(.badURL)
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }

        switch httpResponse.statusCode {
        case 200:
            return data
        case 404:
            throw URLError(.fileDoesNotExist)
        default:
            throw URLError(.badServerResponse)
        }
    }
    
    func uploadSupplementaryFile(forPatientId patientId: Int, fileURL: URL) async throws {
        // Read the raw file data.
        let fileData = try Data(contentsOf: fileURL)
        
        // Use Alamofire's multipart upload.
        let responseData = try await AF.upload(multipartFormData: { mpFD in
            // Append patient_id field.
            if let patientIdData = "\(patientId)".data(using: .utf8) {
                mpFD.append(patientIdData, withName: "patient_id")
            }
            // Append file field with raw binary data.
            mpFD.append(fileData, withName: "file", fileName: fileURL.lastPathComponent)
        }, to: "\(Self.baseURL)/supplemental_materials", method: .post)
        .validate(statusCode: 201..<300)
        .serializingData().value
        
        print("Supplementary file uploaded successfully, response data: \(responseData)")
    }
    
    func deleteSupplementaryFile(fileID: Int) async throws {
        // Construct the full URL using the provided material ID.
        guard let url = URL(string: "\(Self.baseURL)/supplemental_materials/\(fileID)") else {
            throw URLError(.badURL)
        }
        
        // Create a URLRequest and set the HTTP method to DELETE.
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        // Execute the request.
        let (_, response) = try await URLSession.shared.data(for: request)
        
        // Ensure we have a valid HTTP response.
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        // Check the status code to determine whether the deletion was successful.
        switch httpResponse.statusCode {
        case 204:
            print("Supplemental material deleted successfully")
        case 404:
            // You can throw a URLError for a not-found case.
            throw URLError(.fileDoesNotExist)
        case 401:
            // Unauthorized error.
            throw URLError(.userAuthenticationRequired)
        default:
            throw URLError(.badServerResponse)
        }
    }
    
    func fetchSeizures(forPatientId patientId: Int) async throws -> [Seizure] {
        guard let url = URL(string: "\(Self.baseURL)/patients/\(patientId)/seizures") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        guard let seizures = try? decoder.decode([Seizure].self, from: data) else {
            throw URLError(.cannotParseResponse)
        }
        return seizures
    }
    
    func fetchDrugAdministration(forPatientId patientId: Int) async throws -> [DrugAdministration] {
        guard let url = URL(string: "\(Self.baseURL)/patients/\(patientId)/drug_administration") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }

        let decoder = JSONDecoder()
        guard let history = try? decoder.decode([DrugAdministration].self, from: data) else {
            throw URLError(.cannotParseResponse)
        }

        return history
    }
    
    // UNUSED NO API ENDPOINT
    func fetchConversationMessages(forReportId reportId: Int) async throws -> [ChatMessage] {
        guard let url = URL(string: "\(Self.baseURL)/chat/\(reportId)/messages") else {
            throw URLError(.badURL)
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }

        switch http.statusCode {
        case 200:
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let root = try decoder.decode([String: [ChatMessage]].self, from: data)
            return root["messages"] ?? []
        case 401:
            throw URLError(.userAuthenticationRequired)
        case 404:
            throw URLError(.fileDoesNotExist)
        default:
            throw URLError(.badServerResponse)
        }
    }
    
    func sendMessage(toReportId reportId: Int, query: String) async throws -> String {
        guard let url = URL(string: "\(Self.baseURL)/chat/\(reportId)/messages") else {
            throw URLError(.badURL)
        }

        let body = ["query": query]
        let json = try JSONSerialization.data(withJSONObject: body, options: [])

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.httpBody = json

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }

        switch http.statusCode {
        case 200:
            let wrapper = try JSONDecoder().decode([String: String].self, from: data)
            guard let resp = wrapper["response"] else {
                throw URLError(.cannotParseResponse)
            }
            return resp

        case 400:
            throw URLError(.cannotParseResponse)
        case 401:
            throw URLError(.userAuthenticationRequired)
        default:
            throw URLError(.badServerResponse)
        }
    }
    
    func fetchPatientGraph(forPatientId patientId: Int, graphNumber: Int) async throws -> Data {
        guard let url = URL(string: "\(Self.baseURL)/patients/\(patientId)/graph/\(graphNumber)") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let http = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        switch http.statusCode {
        case 200:
            return data
        case 404:
            throw URLError(.fileDoesNotExist)
        default:
            throw URLError(.badServerResponse)
        }
    }
    
    func fetchReportImageIDs(forReportId reportId: Int) async throws -> [Int] {
        guard let url = URL(string: "\(Self.baseURL)/reports/\(reportId)/image_ids") else {
            throw URLError(.badURL)
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        let decoded = try JSONDecoder().decode([String: [Int]].self, from: data)
        return decoded["indexes"] ?? []
    }
    
    func fetchReportImage(imageId: Int) async throws -> (Data, String) {
        guard let url = URL(string: "\(Self.baseURL)/reports/\(imageId)/image") else {
            throw URLError(.badURL)
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("image/jpeg, image/png, image/webp, */*", forHTTPHeaderField: "Accept")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let http = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        switch http.statusCode {
        case 200:
            let mime = response.mimeType
                ?? http.value(forHTTPHeaderField: "Content-Type")?
                    .split(separator: ";", maxSplits: 1)
                    .first
                    .map(String.init)
                ?? "application/octet-stream"
            return (data, mime)
        default:
            throw URLError(.badServerResponse)
        }
    }
}
