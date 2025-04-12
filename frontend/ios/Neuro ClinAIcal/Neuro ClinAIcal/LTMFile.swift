//
//  LTMFile.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/27/25.
//

import SwiftUI

struct LTMFile: Codable {
    let filePath: String
    let fileName: String
    let patientId: Int
    let reportId: Int
    let summary: String
    
    enum CodingKeys: String, CodingKey {
        case filePath = "file_path"
        case fileName = "file_name"
        case patientId = "patient_id"
        case reportId = "report_id"
        case summary = "summary"
    }
}
