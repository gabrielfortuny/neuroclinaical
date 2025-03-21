//
//  Patient.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/4/25.
//

import Foundation
struct Patient: Identifiable {
    let id = UUID()
    let name: String
    var ltmFileLocation: URL? = nil
//    let supplementaryData: [String]? = nil
}
