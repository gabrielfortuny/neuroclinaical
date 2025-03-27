//
//  Session.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/23/25.
//

import SwiftUI

struct Session: Identifiable, Codable {
    let id: Int?
    var ltmFile: URL? = nil
    var supplementaryFiles: [URL] = []
    
    init(id: Int? = nil, ltmFile: URL? = nil, supplementaryFiles: [URL] = []) {
        self.id = id
        self.ltmFile = ltmFile
        self.supplementaryFiles = supplementaryFiles
    }
}
