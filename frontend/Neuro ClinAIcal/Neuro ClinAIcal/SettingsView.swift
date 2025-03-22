//
//  SettingsView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/22/25.
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var session: SessionManager
    @Environment(\.dismiss) var dismiss

    var body: some View {
        VStack(spacing: 20) {
//            Text("Settings")
//                .font(.largeTitle)
//                .padding()

            Button("Log Out") {
                session.logOut()
            }
            .foregroundColor(.red)
            .padding()
            .background(Color.white)
            .cornerRadius(8)
            
            Spacer()
        }
        .padding()
        .navigationTitle("Settings")
        .navigationBarTitleDisplayMode(.inline)
    }
}
