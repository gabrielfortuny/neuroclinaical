//
//  ImageView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/20/25.
//

import SwiftUI

struct ImageView: View {
    @EnvironmentObject var sessionManager: SessionManager
    let imageId: Int

    @State private var uiImage: UIImage? = nil
    @State private var loadError: Error? = nil

    var body: some View {
        Group {
            if let img = uiImage {
                Image(uiImage: img)
                    .resizable()
                    .scaledToFit()
            } else if loadError != nil {
                Text("Failed to load image")
                    .foregroundColor(.red)
            } else {
                ProgressView()
            }
        }
        .task {
            do {
                let (data, _) = try await sessionManager.fetchReportImage(imageId: imageId)
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
