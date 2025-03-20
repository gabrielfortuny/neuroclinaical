//
//  FileView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/15/25.
//

import SwiftUI
import UniformTypeIdentifiers

struct ImportingView: View {
    @State private var importing = false
    
    var body: some View {
        Button("Import") {
            importing = true
        }
        .fileImporter(
            isPresented: $importing,
            allowedContentTypes: [.plainText]
        ) { result in
            switch result {
            case .success(let file):
                print(file.absoluteString)
            case .failure(let error):
                print(error.localizedDescription)
            }
        }
    }
}

//struct TextDocument: FileDocument {
//    static var readableContentTypes: [UTType] {
//        [.plainText]
//    }
//    
//    var text = ""
//    
//    init(text: String) {
//        self.text = text
//    }
//    
//    init(configuration: ReadConfiguration) throws {
//        if let data = configuration.file.regularFileContents {
//            text = String(decoding: data, as: UTF8.self)
//        } else {
//            text = ""
//        }
//    }
//    
//    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
//        FileWrapper(regularFileWithContents: Data(text.utf8))
//    }
//}

//struct ExportingView: View {
//    @State private var exporting = false
//    @State private var document = TextDocument(text: "Hello World")
//    
//    var body: some View {
//        TextEditor(text: $document.text)
//            .toolbar {
//                Button("Export") {
//                    exporting = true
//                }
//                .fileExporter(
//                    isPresented: $exporting,
//                    document: document,
//                    contentType: .plainText
//                ) { result in
//                    switch result {
//                    case .success(let file):
//                        // gain access to the directory
//                        let gotAccess = directory.startAccessingSecurityScopedResource()
//                        if !gotAccess { return }
//                        // access the directory URL
//                        // (read templates in the directory, make a bookmark, etc.)
//                        onTemplatesDirectoryPicked(directory)
//                        // release access
//                        directory.stopAccessingSecurityScopedResource()
//                        print(file)
//                    case .failure(let error):
//                        print(error)
//                    }
//                }
//            }
//    }
//}

#Preview {
    ImportingView()
//    TextDocument(text: "Hello World")
//    ExportingView()
}
