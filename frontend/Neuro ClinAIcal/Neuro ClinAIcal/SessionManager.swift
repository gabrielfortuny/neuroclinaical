//
//  SessionManager.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/22/25.
//

import Foundation

class SessionManager: ObservableObject {
    @Published var currentUser: User? = nil
    
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
}
