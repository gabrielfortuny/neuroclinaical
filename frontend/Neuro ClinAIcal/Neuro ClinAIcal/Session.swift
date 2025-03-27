//
//  Session.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/23/25.
//

import SwiftUI

struct Session: Identifiable, Codable {
    let id: Int?
    var ltmFile: File? = nil
    var supplementaryFiles: [File] = []
    
    init(id: Int? = nil, ltmFile: File? = nil, supplementaryFiles: [File] = []) {
        self.id = id
        self.ltmFile = ltmFile
        self.supplementaryFiles = supplementaryFiles
    }
}
