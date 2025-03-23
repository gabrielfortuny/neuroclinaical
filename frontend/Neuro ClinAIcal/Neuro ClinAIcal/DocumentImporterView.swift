//
//  DocumentImporterView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/20/25.
//
//  NOT IN USE SAMPLE METHOD TO IMPORT

import SwiftUI
import UniformTypeIdentifiers

struct DocumentImporterView: View {
    @Binding var importedFileURL: URL?
    
    @State private var isImporting = false
    
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
        Button("Import File") {
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
    }
}

struct DocumentImporterView_Previews: PreviewProvider {
    static var previews: some View {
        DocumentImporterView(importedFileURL: .constant(nil))
    }
}
