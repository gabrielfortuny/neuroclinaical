//
//  PatientView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/14/25.
//

import SwiftUI
import UniformTypeIdentifiers

enum InfoOption: Equatable {
    case viewFile
    case data
    case summary
    case askQuestion

    var title: String {
        switch self {
            case .viewFile: return "View File"
            case .data: return "Data"
            case .summary: return "Summary"
            case .askQuestion: return "Ask Question"
        }
    }
}

struct PatientView: View {
    @EnvironmentObject private var sessionManager: SessionManager
    var patient: Patient
    
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    @State private var selectedTab: InfoOption = .viewFile
    @Environment(\.presentationMode) var presentationMode
    @State private var expandedSessionID: Int? = nil
    
    @State private var importedFileURL: URL? = nil
    @State private var isImportingLTMFile = false
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
    @State private var isImportingSupplementary = false
    
    @State private var sessions: [Session] = [Session(id: 0)]
    @State private var summary: String? = nil

    // Function for bottom navigation buttons
    func tabButton(icon: String, option: InfoOption, isSelected: Bool) -> some View {
        Button(action: {
            selectedTab = option
        }) {
            VStack {
                Image(systemName: icon)
                    .font(.system(size: 24))
                    .foregroundColor(.white)

                Text(option.title)
                    .font(.footnote)
                    .foregroundColor(.white)
            }
                .padding()
                .background(Color.clear)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.white, lineWidth: 2)
                )
        }
        .frame(maxWidth: .infinity)
    }
    
    @ViewBuilder
    private func renderOption(_ option: InfoOption) -> some View {
        switch option {
            case InfoOption.viewFile:
                viewFileContent()
            case InfoOption.data:
                dataContent()
            case InfoOption.summary:
                summaryContent()
            case InfoOption.askQuestion:
                askQuestionContent()
        }
    }
    
    private func askQuestionContent() -> some View {
        ScrollView {
            Text("Ask Question MVP")
        }
    }
    
    private func summaryContent() -> some View {
        ScrollView {
            Text("Summary")
        }
    }
    
    private func dataContent() -> some View {
        ScrollView {
            Text("Data")
        }
    }
    
    private func importFileButton() -> some View {
        Button("Import File") {
            isImportingLTMFile = true
        }
        .foregroundColor(.blue)
        .fileImporter(
            isPresented: $isImportingLTMFile,
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
    
    private func renderLTMFile(_ session: Session) -> some View {
        VStack {
            HStack {
                Text("Long Term Monitoring Report")
                    .font(.headline)
                    .foregroundColor(.black)
                Spacer()
            }
            Divider()
                .background(Color.gray)
            
            HStack {
                if let file = session.ltmFile {
                    Text(file.filePath)
                        .foregroundColor(.blue)
                        .underline()
                    Spacer()
                    Button {
                        Task {
                            do {
                                try await sessionManager.deleteReport(reportId: file.reportId)
                                try await refresh()
                            } catch {
                                print("Error deleting report: \(error)")
                            }
                        }
                    } label: {
                        Image(systemName: "trash")
                            .foregroundColor(.red)
                    }
                } else {
                    Text("No LTM added")
                        .foregroundColor(.gray)
                    Spacer()
                    importFileButton()
                    .onChange(of: importedFileURL) { oldValue, newValue in
                        if let newValue = newValue {
                            Task {
                                do {
                                    print("Uploading LTM Report: \(newValue)")
                                    try await sessionManager.uploadReport(forPatientId: patient.id, fileURL: newValue)
                                    try await refresh()
                                } catch {
                                    print("Error uploading report: \(error)")
                                }
                            }
                            importedFileURL = nil
                        }
                    }
                }
            } // HStack 2
        } // VStack
        .padding()
    }
    
    /*private func renderSupplementaryFiles(_ session: Session) -> some View {
        // Start Supplementary File Code
        VStack (alignment: .leading, spacing: 8) {
            HStack {
                Text("Supplementary Files")
                    .font(.headline)
                    .foregroundColor(.black)
                Spacer()
            }
            Divider()
                .background(Color.gray)
            
            ForEach(supplementaryFiles, id: \.id) { file in
                HStack {
                    Text(file.url.lastPathComponent)
                        .foregroundColor(.blue)
                        .underline()
                    Spacer()
                    Button {
                        if let index = patient.sessions.firstIndex(where: { $0.id == session.id }) {
                            patient.sessions[index].supplementaryFiles.removeAll(where: { $0.id == file.id })
                        }
                    } label: {
                        Image(systemName: "trash")
                            .foregroundColor(.red)
                    }
                }
            }
            
            Button("Add New File") {
                isImportingSupplementary = true
            }
            .foregroundColor(.blue)
            .fileImporter(
                isPresented: $isImportingSupplementary,
                allowedContentTypes: allowedTypes,
                allowsMultipleSelection: false
            ) { result in
                switch result {
                case .success(let urls):
                    if let url = urls.first {
//                        if let index = patient.sessions.firstIndex(where: { $0.id == session.id }) {
//                            patient.sessions[index].supplementaryFiles.append(File(id: /* provide an id */, url: url))
//                        }
                        print("Upload Supplementary File Success: \(url.absoluteString)")
                    }
                case .failure(let error):
                    print("Supplementary file import error: \(error.localizedDescription)")
                }
            }
        }
        .padding()
        // End Supplementary File Code
    }*/
    
    @ViewBuilder
    private func viewFileContent() -> some View {
        ForEach (Array(sessions)) {
            session in ScrollView {
                /*HStack {
                    Text("Session \(index + 1)")
                        .foregroundColor(.black)
                    Spacer()
                    Image(systemName: expandedSessionID == session.id ? "minus.circle" : "plus.circle")
                        .foregroundColor(.black)
                }
                .padding(.horizontal, 10)
                .font(.title2)*/
                
                // Supossed to be expandedSessionID == session.id
                if session.id == session.id {
                    renderLTMFile(session)
//                        renderSupplementaryFiles(session)
//                    Spacer()
                           
                    /*Button("Delete Session") {
                        patient.deleteSession(withId: session.id)
                        expandedSessionID = nil
                    }
                    .font(.headline)
                    .padding(10)
                    .foregroundColor(.red)
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(5)
                    .frame(alignment: .center)*/
                }
            } // ScrollView
            .background(Color.white)
            /*.onTapGesture {
                if expandedSessionID == session.id {
                    expandedSessionID = nil
                } else {
                    expandedSessionID = session.id
                }
            }*/
        } // ForEach

        /*Button(action: {
            patient.sessions.append(Session())
        }) {
            Text("Add Session")
                .font(.headline)
                .foregroundColor(.black)
                .frame(maxWidth: 150, minHeight: 50)
                .background(Color.white)
                .cornerRadius(8)
        }*/
    } // viewFileContet()
    
    private func refresh() async throws {
        sessions[0].ltmFile = try await sessionManager.fetchFirstReportID(forPatientId: patient.id)
        print("LTM File Location (refresh): \(sessions[0].ltmFile?.filePath ?? "Not Found")")
    }
    
    var body: some View {
        ZStack {
            backgroundColor.edgesIgnoringSafeArea(.all)

            VStack {
                Text("Patient: \(patient.name)")
                    .font(.largeTitle)
                    .foregroundColor(.white)
                                
                renderOption(selectedTab)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.white)
                    .cornerRadius(12)
                    .padding(.horizontal)
                
                // Bottom Navigation Bar
                HStack {
                    tabButton(icon: "doc.text", option: .viewFile, isSelected: selectedTab == .viewFile)
                    tabButton(icon: "chart.bar", option: .data, isSelected: selectedTab == .data)
                    tabButton(icon: "doc.plaintext", option: .summary, isSelected: selectedTab == .summary)
                    tabButton(icon: "brain.head.profile", option: .askQuestion, isSelected: selectedTab == .askQuestion)
                }
                .padding(.horizontal, 10)
            }
        }
        .navigationBarBackButtonHidden(true)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button(action: { presentationMode.wrappedValue.dismiss() }) {
                    HStack {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                        Text("Back")
                            .foregroundColor(.white)
                    }
                }
            }
        }
        .toolbarBackground(.hidden, for: .navigationBar)
        .task {
            do {
                try await refresh()
            } catch {
                print("Error fetching report: \(error)")
            }
        }
    }
}

struct PatientView_Previews: PreviewProvider {
    static var previews: some View {
        let session = SessionManager()
        session.logIn(email: "Demo@example.com", password: "123")
        let patient = Patient(id: 1, name: "John")
        return NavigationStack {
            PatientView(patient: patient)
                .environmentObject(session)
        }
    }
}
