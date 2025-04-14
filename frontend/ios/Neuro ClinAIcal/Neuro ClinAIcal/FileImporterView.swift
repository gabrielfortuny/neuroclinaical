//
//  FileImporterView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/14/25.
//

import SwiftUI
import UniformTypeIdentifiers

struct FileImporterView: View {
    @Binding var importedFileURL: URL?
    var allowedTypes: [UTType]
    var buttonTitle: String
    var onFileImported: (URL) async throws -> Void

    @State private var isImporting = false

    var body: some View {
        Button(buttonTitle) {
            isImporting = true
        }
        .foregroundColor(.blue)
        .fileImporter(
            isPresented: $isImporting,
            allowedContentTypes: allowedTypes,
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                if let url = urls.first {
                    importedFileURL = url
                    print("Imported file: \(url.absoluteString)")
                }
            case .failure(let error):
                print("File import error: \(error.localizedDescription)")
            }
        }
        .onChange(of: importedFileURL) { _, newValue in
            if let newValue = newValue {
                Task {
                    do {
                        try await onFileImported(newValue)
                    } catch {
                        print("Error uploading file: \(error)")
                    }
                }
                // Reset the binding to allow reupload later.
                importedFileURL = nil
            }
        }
    }
}
