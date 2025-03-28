//
//  LTMFile.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/27/25.
//

import SwiftUI

struct LTMFile: Codable {
    let createdAt: String
    let filePath: String
    let fileType: String
    let modifiedAt: String
    let patientId: Int
    let reportId: Int
    let summary: String
    
    enum CodingKeys: String, CodingKey {
        case createdAt = "created_at"
        case filePath = "filepath"
        case fileType = "filetype"
        case modifiedAt = "modified_at"
        case patientId = "patient_id"
        case reportId = "report_id"
        case summary
    }
}
