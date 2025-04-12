//
//  Session.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/23/25.
//

import SwiftUI

struct Session: Identifiable, Codable {
    let id: Int?
    var ltmFile: LTMFile? = nil
//    var supplementaryFiles: [File] = []
}
