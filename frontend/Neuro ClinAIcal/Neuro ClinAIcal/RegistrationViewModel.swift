import SwiftUI
import Combine

class RegistrationViewModel: ObservableObject {
    // Input fields
    @Published var username: String = ""
    @Published var email: String = ""
    @Published var password: String = ""
    @Published var confirmPassword: String = ""
    
    // UI state
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil
    @Published var showSuccess: Bool = false
    
    private let session: SessionManager  // ✅ Injected manually now
    private var cancellables = Set<AnyCancellable>()
    
    init(session: SessionManager) {
        self.session = session
    }
    
    private let registrationURL = URL(string: "http://192.168.1.76:5050/users/register")!
    
    func register() {
        errorMessage = nil
        
        guard !username.isEmpty, !email.isEmpty, !password.isEmpty, !confirmPassword.isEmpty else {
            errorMessage = "All fields are required."
            return
        }
        guard password == confirmPassword else {
            errorMessage = "Passwords do not match."
            return
        }
        
        let payload: [String: Any] = [
            "username": username,
            "name": username,
            "email": email,
            "password": password
        ]
        
        guard let jsonData = try? JSONSerialization.data(withJSONObject: payload) else {
            errorMessage = "Failed to create request payload."
            return
        }
        
        var request = URLRequest(url: registrationURL)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        isLoading = true
        
        URLSession.shared.dataTaskPublisher(for: request)
            .tryMap { data, response -> Data in
                if let httpResponse = response as? HTTPURLResponse {
                    print("📡 Response status code: \(httpResponse.statusCode)")
                }
                let body = String(data: data, encoding: .utf8) ?? "Unable to decode response body"
                print("📩 Response body: \(body)")
                
                guard let httpResponse = response as? HTTPURLResponse,
                      (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
                return data
            }
            .decode(type: RegistrationResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                guard let self = self else { return }
                self.isLoading = false
                if case .failure(let error) = completion {
                    if let urlError = error as? URLError {
                        self.errorMessage = "Network error: \(urlError.localizedDescription)"
                    } else {
                        self.errorMessage = "Registration failed. Please try again."
                    }
                }
            } receiveValue: { [weak self] registrationResponse in
                guard let self = self else { return }
                UserDefaults.standard.set(registrationResponse.token, forKey: "authToken")
                self.session.logInDirect(username: self.username, email: self.email)
            }
            .store(in: &cancellables)
    }
}

struct RegistrationResponse: Codable {
    let token: String
}
