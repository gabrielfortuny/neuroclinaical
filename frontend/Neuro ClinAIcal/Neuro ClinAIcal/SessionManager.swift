//
//  SessionManager.swift
//  Neuro ClinAIcal
//

import Foundation

class SessionManager: ObservableObject {
    @Published var currentUser: User? = nil
    
    var users: [User] = [
        User(id: 0, username: "Demo", email: "Demo@example.com")
    ]
    
    // MARK: - For demo logins
    private func authenticateUser(email: String, password: String) -> User? {
        if email == "Demo@example.com" && password == "123" {
            return users.first(where: { $0.id == 0 })
        }
        return nil
    }
    
    func logIn(email: String, password: String) {
        if let user = authenticateUser(email: email, password: password) {
            currentUser = user
        }
    }

    // NEW: Log in using known user info (used after registration)
    func logInDirect(username: String, email: String) {
        let newUser = User(id: UUID().hashValue, username: username, email: email)
        currentUser = newUser
    }

    func logOut() {
        currentUser = nil
    }
}
