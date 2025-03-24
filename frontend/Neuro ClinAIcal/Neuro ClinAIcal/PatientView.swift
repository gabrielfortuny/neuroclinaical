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
    @EnvironmentObject var sessionManager: SessionManager
    @Binding var patient: Patient
    
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    @State private var selectedTab: InfoOption = .viewFile
    @Environment(\.presentationMode) var presentationMode
    @State private var expandedSessionID: UUID? = nil
    
    @State private var isImportingLTMFile = false
    @State private var importedFileURL: URL? = nil
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
    
    var sessions: [String] = []
    var data: [String] = []
    var summary: String? = nil

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
            case .viewFile:
                viewFileContent()
            case .data:
                dataContent()
            case .summary:
                summaryContent()
            case .askQuestion:
                askQuestionContent()
        }
    }
    
    @ViewBuilder
    private func askQuestionContent() -> some View {
        ScrollView {
            Text("Ask Question MVP")
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.white)
        .cornerRadius(12)
        .padding(.horizontal, 20)
    }
    
    @ViewBuilder
    private func summaryContent() -> some View {
        ScrollView {
            Text("Summary")
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.white)
        .cornerRadius(12)
        .padding(.horizontal, 20)    }
    
    @ViewBuilder
    private func dataContent() -> some View {
        ScrollView {
            Text("Data")
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.white)
        .cornerRadius(12)
        .padding(.horizontal, 20)
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
    
    @ViewBuilder
    private func viewFileContent() -> some View {
        VStack {
            ForEach (Array(patient.sessions.enumerated()), id: \.element.id) { index, session in
                VStack {
                    HStack {
                        Text("Session \(index + 1)")
                            .foregroundColor(.black)
                        Spacer()
                        Image(systemName: expandedSessionID == session.id ? "minus.circle" : "plus.circle")
                            .foregroundColor(.black)
                    }
                    .padding(.horizontal, 10)
                    .font(.title2)
                    
                    if expandedSessionID == session.id {
                        // Start LTM File Code
                        VStack(alignment: .leading, spacing: 8) {
                            // Title with a line underneath
                            HStack {
                                Text("Long Term Monitoring Report")
                                    .font(.headline)
                                    .foregroundColor(.black)
                                Spacer()
                            }
                            Divider()
                                .background(Color.gray)
                            
                            if let file = session.ltmFile {
                                // If a file exists, display its name with a link icon.
                                HStack {
                                    Text(file.lastPathComponent)
                                        .foregroundColor(.blue)
                                        .underline()
                                    Spacer()
                                    Button {
                                        if let index = patient.sessions.firstIndex(where: { $0.id == session.id }) {
                                            patient.sessions[index].ltmFile = nil
                                        }
                                    } label: {
                                        Image(systemName: "trash")
                                            .foregroundColor(.red)
                                    }
                                    
                                }
                            } else {
                                // If no file, show "No LTM added" with an Import button.
                                HStack {
                                    Text("No LTM added")
                                        .foregroundColor(.gray)
                                    Spacer()
                                    importFileButton()
                                    .onChange(of: importedFileURL) { newValue, _ in
                                        if let index = patient.sessions.firstIndex(where: { $0.id == session.id }) {
                                            patient.sessions[index].ltmFile = newValue
                                            importedFileURL = nil
                                        }
                                    }
                                }
                            }
                        }
                        .padding()
                        // End LTM File Code
                        
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
                            
                            ForEach(session.supplementaryFiles, id: \.self) { file in
                                HStack {
                                    Text(file.lastPathComponent)
                                        .foregroundColor(.blue)
                                        .underline()
                                    Spacer()
                                    Button {
                                        if let index = patient.sessions.firstIndex(where: { $0.id == session.id }) {
                                            patient.sessions[index].supplementaryFiles.removeAll(where: { $0 == file })
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
                                    if let url = urls.first,
                                       let index = patient.sessions.firstIndex(where: { $0.id == session.id }) {
                                        patient.sessions[index].supplementaryFiles.append(url)
                                    }
                                case .failure(let error):
                                    print("Supplementary file import error: \(error.localizedDescription)")
                                }
                            }
                        }
                        .padding()
                        // End Supplementary File Code
                        
                        
                        Button("Delete Session") {
                            patient.deleteSession(withId: session.id)
                            expandedSessionID = nil
                        }
                        .font(.headline)
                        .padding(10)
                        .foregroundColor(.red)
                        .background(Color.gray.opacity(0.2))
                        .cornerRadius(5)
                        .frame(alignment: .center)
                    }
                }
                .frame(maxWidth: .infinity, minHeight: expandedSessionID == session.id ? 100 : 50)
                .background(Color.white)
                .cornerRadius(8)
                .onTapGesture {
                    if expandedSessionID == session.id {
                        expandedSessionID = nil
                    } else {
                        expandedSessionID = session.id
                    }
                }
            }
        }
        .padding(.horizontal, 10)
        
        Spacer()
        
        Button(action: {
            patient.sessions.append(Session())
        }) {
            Text("Add Session")
                .font(.headline)
                .foregroundColor(.black)
                .frame(maxWidth: 150, minHeight: 50)
                .background(Color.white)
                .cornerRadius(8)
        }
    }
    
    var body: some View {
        ZStack {
            backgroundColor.edgesIgnoringSafeArea(.all)

            VStack {
                Text("Patient: \(patient.name)")
                    .font(.largeTitle)
                    .foregroundColor(.white)
                                
                renderOption(selectedTab)
                
                // Bottom Navigation Bar
                HStack {
                    tabButton(icon: "doc.text", option: .viewFile, isSelected: selectedTab == .viewFile)
                    tabButton(icon: "chart.bar", option: .data, isSelected: selectedTab == .data)
                    tabButton(icon: "doc.plaintext", option: .summary, isSelected: selectedTab == .summary)
                    tabButton(icon: "brain.head.profile", option: .askQuestion, isSelected: selectedTab == .askQuestion)
                }
                .padding(.horizontal, 20)
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
    }
}



struct PatientViewInteractivePreview: View {
    @State var patient = Patient(name: "John Doe")
    let session: SessionManager = {
             let s = SessionManager()
             s.logIn(email: "Demo@example.com", password: "123")
             return s
        }()

    var body: some View {
        NavigationStack {
            PatientView(patient: $patient)
                .environmentObject(session)
        }
    }
}

struct PatientView_Previews: PreviewProvider {
    static var previews: some View {
        PatientViewInteractivePreview()
    }
}
