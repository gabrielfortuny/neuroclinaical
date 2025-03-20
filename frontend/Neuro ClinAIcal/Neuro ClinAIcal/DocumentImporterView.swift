//
//  DocumentImporterView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/20/25.
//

import SwiftUI
import UniformTypeIdentifiers

struct DocumentImporterView: View {
    @State private var isImporting = false
    @State private var importedFileURL: URL?
    
    // Computed property to build allowed file types dynamically.
    var allowedTypes: [UTType] {
        var types: [UTType] = [.pdf]
        // For DOC files:
        if let docType = UTType("com.microsoft.word.doc") {
            types.append(docType)
        }
        // For DOCX files:
        if let docxType = UTType("org.openxmlformats.wordprocessingml.document") {
            types.append(docxType)
        }
        return types
    }
    
    var body: some View {
        VStack(spacing: 20) {
            if let url = importedFileURL {
                Text("Imported file: \(url.lastPathComponent)")
                    .padding()
            } else {
                Text("No file imported yet.")
                    .padding()
            }
            
            Button("Import Document") {
                isImporting = true
            }
            .padding()
        }
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
    }
}

struct DocumentImporterView_Previews: PreviewProvider {
    static var previews: some View {
        DocumentImporterView()
    }
}
