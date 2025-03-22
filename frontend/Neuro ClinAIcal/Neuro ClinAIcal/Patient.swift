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
    var ltmFileLocation: URL?
//    let supplementaryData: [String]? = nil
    
    init(id: UUID = UUID(), name: String, ltmFileLocation: URL? = nil) {
        self.id = id
        self.name = name
        self.ltmFileLocation = ltmFileLocation
    }
}
