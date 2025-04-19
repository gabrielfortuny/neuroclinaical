//
//  SupplementaryFile.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/12/25.
//

struct SupplementaryFile: Codable, Identifiable {
    let id: Int
    let filepath: String

    enum CodingKeys: String, CodingKey {
        case id
        case filepath = "file_path"
    }
}
