//
//  File.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/27/25.
//

import SwiftUI

struct File: Identifiable, Codable, Hashable {
    let id: Int
    let url: URL
    
    init(id: Int, url: URL) {
        self.id = id
        self.url = url
    }
}
