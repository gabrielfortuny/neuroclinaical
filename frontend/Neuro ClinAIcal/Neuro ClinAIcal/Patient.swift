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
    let age: Int
}
