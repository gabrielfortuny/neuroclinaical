//
//  Session.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/23/25.
//

struct Session: Identifiable, Codable {
    let id: Int
    var ltmFile: LTMFile? = nil
    var supplementaryFiles: [SupplementaryFile] = []
    // var seizures: [Seizure] = []
    // var drugAdministrations: [DrugAdministration] = []
    // var chatMessages: [ChatMessage] = [] // UNUSED NO API ENDPOINT
}
