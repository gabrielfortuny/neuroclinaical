//
//  DocumentPicker.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/14/25.
//

import SwiftUI
import UniformTypeIdentifiers

struct DocumentPicker: UIViewControllerRepresentable {
    let allowedTypes: [UTType]
    let asCopy: Bool
    let onPick: ([URL]) -> Void
    func makeCoordinator() -> Coordinator {
        Coordinator(onPick: onPick, asCopy: asCopy)
    }
    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let vc = UIDocumentPickerViewController(
            forOpeningContentTypes: allowedTypes,
            asCopy: asCopy
        )
        vc.delegate = context.coordinator
        return vc
    }
    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController,
                                context: Context) {}
    class Coordinator: NSObject, UIDocumentPickerDelegate {
        let onPick: ([URL]) -> Void
        let asCopy: Bool
        init(onPick: @escaping ([URL]) -> Void, asCopy: Bool) {
            self.onPick = onPick
            self.asCopy = asCopy
        }
        func documentPicker(_ controller: UIDocumentPickerViewController,
                            didPickDocumentsAt urls: [URL]) {
            if !asCopy {
                // start security‑scope so you can read in place
                for url in urls { _ = url.startAccessingSecurityScopedResource() }
            }
            onPick(urls)
            // you can stopAccessing in your upload logic
        }
    }
}
