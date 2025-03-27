//
//  Patient.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/4/25.
//

import Foundation

struct Patient: Identifiable, Codable {
    let id: Int
    let name: String
    var sessions: [Session]
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        // If sessions key is missing, default to an empty array.
        sessions = try container.decodeIfPresent([Session].self, forKey: .sessions) ?? [Session()]
    }
    
    // Shouldn't be used since patients are always populated through a request
//    init(id: Int, name: String, sessions: [Session] = [Session()]) {
//        self.id = id
//        self.name = name
//        self.sessions = sessions
//    }
    
    // Should make an api request
//    mutating func deleteSession(withId id: Int) {
//        if let index = sessions.firstIndex(where: { $0.id == id }) {
//            sessions.remove(at: index)
//        }
//    }
}
