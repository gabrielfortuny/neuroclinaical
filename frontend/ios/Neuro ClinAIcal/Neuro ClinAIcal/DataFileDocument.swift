//
//  DataFileDocument.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 4/18/25.
//

import SwiftUI
import UniformTypeIdentifiers

struct DataFileDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.data] }

    var data: Data

    init(data: Data = Data()) {
        self.data = data
    }

    init(configuration: ReadConfiguration) throws {
        self.data = configuration.file.regularFileContents ?? Data()
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        FileWrapper(regularFileWithContents: data)
    }
}
