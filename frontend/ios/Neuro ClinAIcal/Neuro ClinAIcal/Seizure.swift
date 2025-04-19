//
//  Seizure.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/16/25.
//

import Foundation

struct Electrode: Identifiable, Codable {
    let id: Int
    let name: String
    let createdAt: Date
    let modifiedAt: Date

    enum CodingKeys: String, CodingKey {
        case id, name
        case createdAt   = "created_at"
        case modifiedAt  = "modified_at"
    }
}

struct Seizure: Identifiable, Codable {
    let id: Int
    let day: Int
    let startTime: String    // "HH:MM:SS"
    let duration: String     // SQL interval string, e.g. "00:02:30"
    let createdAt: Date
    let modifiedAt: Date
    let electrodes: [Electrode]

    enum CodingKeys: String, CodingKey {
        case id, day, duration, electrodes
        case startTime  = "start_time"
        case createdAt  = "created_at"
        case modifiedAt = "modified_at"
    }
}
