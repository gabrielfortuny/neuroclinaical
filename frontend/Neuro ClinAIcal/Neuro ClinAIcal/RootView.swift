//
//  RootView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/22/25.
//

import SwiftUI

struct RootView: View {
    @EnvironmentObject var session: SessionManager
    
    var body: some View {
        if session.currentUser == nil {
            SignInView()
                .environmentObject(session)
        } else {
            MainView()
                .environmentObject(session)
        }
    }
}
