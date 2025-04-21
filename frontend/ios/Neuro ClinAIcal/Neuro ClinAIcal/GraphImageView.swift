//
//  GraphImageView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/21/25.
//

import SwiftUI

struct GraphImageView: View {
    @EnvironmentObject var sessionManager: SessionManager
    let patientId: Int
    let graphNumber: Int

    @State private var uiImage: UIImage? = nil
    @State private var loadError: Error? = nil

    var body: some View {
        Group {
            if let img = uiImage {
                Image(uiImage: img)
                    .resizable()
                    .scaledToFit()
            } else if loadError != nil {
                Text("Failed to load")
                    .foregroundColor(.red)
            } else {
                ProgressView()
            }
        }
        .task {
            do {
                let data = try await sessionManager.fetchPatientGraph(
                    forPatientId: patientId,
                    graphNumber: graphNumber
                )
                guard let img = UIImage(data: data) else {
                    throw URLError(.cannotDecodeContentData)
                }
                uiImage = img
            } catch {
                loadError = error
            }
        }
    }
}
