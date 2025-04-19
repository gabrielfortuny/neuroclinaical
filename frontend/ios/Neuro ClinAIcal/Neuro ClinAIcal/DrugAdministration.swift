//
//  DrugAdministration.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/16/25.
//

struct DrugAdministration: Identifiable, Codable {
    let id: Int
    let drugId: Int
    let drugName: String
    let drugClass: String
    let day: Int
    let dosage: Int
    let time: String        // "HH:MM:SS"

    enum CodingKeys: String, CodingKey {
        case id, day, dosage, time
        case drugId    = "drug_id"
        case drugName  = "drug_name"
        case drugClass = "drug_class"
    }
}
