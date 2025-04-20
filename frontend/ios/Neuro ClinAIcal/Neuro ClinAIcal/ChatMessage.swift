//
//  ChatMessage.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/19/25.
//

// UNUSED NO API ENDPOINT

import Foundation

struct ChatMessage: Identifiable, Codable {
    let id: Int
    let query: String
    let response: String
    let createdAt: Date?

    enum CodingKeys: String, CodingKey {
        case id, query, response
        case createdAt = "created_at"
    }
}
