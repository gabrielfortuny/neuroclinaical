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

enum FileType: Equatable {
    case report
    case supplemental
}

struct PatientView: View {
    @EnvironmentObject private var sessionManager: SessionManager
    var patient: Patient
    
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    @State private var selectedTab: InfoOption = .viewFile
    @Environment(\.presentationMode) var presentationMode
    
    @State private var importedReportURL: URL? = nil
    @State private var importedSupplementalURL: URL? = nil
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
    
    @State private var documentToExport: DataFileDocument? = nil
    @State private var exportFilename: String = ""
    @State private var showingExporter = false
    
    @State private var query: String = ""
    @State private var question: String = ""
    @State private var response: String = ""
    
    @State private var session: Session = Session(id: 0)

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
            if let file = session.ltmFile {
                HStack {
                    TextField("Type your question…", text: $query)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    Button("Send") {
                        let userText = query.trimmingCharacters(in: .whitespacesAndNewlines)
                        guard !userText.isEmpty else { return }
                        query = ""
                        Task {
                            do {
                                question = userText
                                response = try await sessionManager.sendMessage(
                                    toReportId: file.reportId,
                                    query: userText
                                )
                            } catch {
                                print("Error sending message:", error)
                            }
                        } // Task
                    } // Button
                    .disabled(query.isEmpty)
                } // HStack
                
                Divider()
                
                if response.isEmpty {
                    Text("Ask a question...").foregroundColor(.gray)
                } else {
                    Text("Question:")
                        .font(.title)
                    Text(question)
                    Text("Answer:")
                        .font(.title)
                    Text("\(.init(response))")
                }
            } else {
                Text("No Long Term Monitoring Report")
            }
        }
        .padding()
    }
    
    private func summaryContent() -> some View {
        ScrollView {
            if let ltmFile = session.ltmFile {
                Text(.init(ltmFile.summary))
            } else {
                Text("No Long Term Monitoring Report")
            }
        }
        .padding()
    }
    
    private func dataContent() -> some View {
        ScrollView {
            if let _ = session.ltmFile {
                Text("Show graphs here")
            } else {
                Text("No Long Term Monitoring Report")
            }
        }
        .padding()
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
                    if let fileName = file.filePath.split(separator: "/").last {
                        Text(fileName)
                            .foregroundColor(.blue)
                            .underline()
                            .onTapGesture {
                                print("Tapped LTM File")
                                Task {
                                    do {
                                        let data = try await sessionManager.downloadReport(reportId: file.reportId)
                                        exportFilename = String(fileName)
                                        documentToExport = DataFileDocument(data: data)
                                        showingExporter = true
                                    } catch {
                                        print("Error downloading report: \(error)")
                                    }
                                }
                            }
                    }
                    Spacer()
                    Button {
                        Task {
                            do {
                                try await sessionManager.deleteReport(reportId: file.reportId)
                                await refresh()
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
                    FileImporterView(importedFileURL: $importedReportURL,
                                   allowedTypes: allowedTypes,
                                   buttonTitle: "Import LTM") { fileURL in
                        try await sessionManager.uploadReport(forPatientId: patient.id, fileURL: fileURL)
                        await refresh()
                    }
                }
            } // HStack 2
        } // VStack
        .padding()
    }
    
    private func renderSupplementaryFiles(_ session: Session) -> some View {
        VStack (alignment: .leading, spacing: 8) {
            HStack {
                Text("Supplementary Files")
                    .font(.headline)
                    .foregroundColor(.black)
                Spacer()
            }
            Divider()
                .background(Color.gray)
            
            ForEach(session.supplementaryFiles) { file in
                HStack {
                    if let fileName = file.filepath.split(separator: "/").last {
                        Text(fileName)
                            .foregroundColor(.blue)
                            .underline()
                            .onTapGesture {
                                print("Tapped LTM File")
                                Task {
                                    do {
                                        let data = try await sessionManager.downloadSupplementalMaterial(materialId: file.id)
                                        exportFilename = String(fileName)
                                        documentToExport = DataFileDocument(data: data)
                                        showingExporter = true
                                    } catch {
                                        print("Error downloading report: \(error)")
                                    }
                                }
                            }
                    }
                    Spacer()
                    Button {
                        Task {
                            do {
                                try await sessionManager.deleteSupplementaryFile(fileID: file.id)
                                await refresh()
                            } catch {
                                print("Error deleting report: \(error)")
                            }
                        }
                    } label: {
                        Image(systemName: "trash")
                            .foregroundColor(.red)
                    }
                }
            }
            
            FileImporterView(importedFileURL: $importedSupplementalURL,
               allowedTypes: allowedTypes,
               buttonTitle: "Add New File") { fileURL in
                try await sessionManager.uploadSupplementaryFile(forPatientId: patient.id, fileURL: fileURL)
                await refresh()
            }
        }
        .padding()
    }
    
    @ViewBuilder
    private func viewFileContent() -> some View {
        ScrollView {
                renderLTMFile(session)
                renderSupplementaryFiles(session)
            } // ScrollView
            .background(Color.white)
    } // viewFileContet()
    
    private func refresh() async {
        do {
            session.ltmFile = try await sessionManager.fetchFirstReportID(forPatientId: patient.id)
        } catch {
            print("Failed to fetch LTM file:", error)
        }
        do {
            session.supplementaryFiles = try await sessionManager.fetchSupplementalMaterials(forPatientId: patient.id)
        } catch {
            print("Failed to fetch supplementary materials:", error)
        }
        /*do {
            session.seizures = try await sessionManager.fetchSeizures(forPatientId: patient.id)
        } catch {
            print("Failed to fetch seizures:", error)
        }
        do {
            session.drugAdministrations = try await sessionManager.fetchDrugAdministration(forPatientId: patient.id)
        } catch {
            print("Failed to fetch drug administrations:", error)
        }
        if let reportID = session.ltmFile?.reportId {
            do {
                session.chatMessages = try await sessionManager.fetchConversationMessages(forReportId: reportID)
            } catch {
                print("Failed to fetch chat messages:", error)
            }
        }*/
        print("Ran Refresh")
        print("LTM ID: \(session.ltmFile!.reportId)")
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
            await refresh()
        }
        .fileExporter(
          isPresented: $showingExporter,
          document: documentToExport,
          contentType: .data,
          defaultFilename: exportFilename
        ) { result in
          switch result {
          case .success:
            print("User chose a location and saved the file.")
          case .failure(let err):
            print("Export failed:", err)
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
