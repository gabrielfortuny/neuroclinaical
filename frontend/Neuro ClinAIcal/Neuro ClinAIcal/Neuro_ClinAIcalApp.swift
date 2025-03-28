//
//  Neuro_ClinAIcalApp.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/4/25.
//

import SwiftUI

@main
struct Neuro_ClinAIcalApp: App {
    @StateObject private var session = SessionManager()
        
    var body: some Scene {
        WindowGroup {
            if session.currentUser == nil {
                SignInView()
                    .environmentObject(session)
            } else {
                MainView()
                    .environmentObject(session)
            }
        }
    }
}
