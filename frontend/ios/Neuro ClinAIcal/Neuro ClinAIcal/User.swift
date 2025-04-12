//
//  Session.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/22/25.
//

struct User: Identifiable, Codable {
    let id: Int
    let username: String
    let email: String
    var patientIDs: [Int] = []
}
