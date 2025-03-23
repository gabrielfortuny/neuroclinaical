//
//  Patient.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/4/25.
//

import Foundation

struct Patient: Identifiable, Codable {
    let id: UUID
    let name: String
    var sessions: [Session] = []
    
    init(id: UUID = UUID(), name: String, sessions: [Session] = []) {
        self.id = id
        self.name = name
        self.sessions = sessions
    }
    
    mutating func deleteSession(withId id: UUID) {
        if let index = sessions.firstIndex(where: { $0.id == id }) {
            sessions.remove(at: index)
        }
    }
}
