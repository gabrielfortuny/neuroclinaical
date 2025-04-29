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
  let onLoad: () -> Void

  @State private var uiImage: UIImage?
  @State private var loadError: Error?
  @State private var hasFired = false

  var body: some View {
    Group {
      if let img = uiImage {
        ScrollView(.horizontal) {
          Image(uiImage: img)
            .interpolation(.high)
            .antialiased(false)
        }
        .onAppear {
          // once we actually display it, fire the onLoad exactly once
          guard !hasFired else { return }
          hasFired = true
          onLoad()
        }
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
