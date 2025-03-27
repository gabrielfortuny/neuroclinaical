//
//  PatientView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/14/25.
//

import SwiftUI

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

enum DataSubOption: Equatable {
    case seizureGraph
    case withSOZ
    case withDrug

    var title: String {
        switch self {
        case .seizureGraph: return "Seizure graph"
        case .withSOZ:      return "with SOZ info"
        case .withDrug:     return "with drug info"
        }
    }
}

struct PatientView: View {
    @Binding var patient: Patient
    
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    
    @State private var selectedTab: InfoOption = .viewFile
    @State private var selectedDataTab: DataSubOption = .seizureGraph
    
    @State private var seizureGraphHeatmap: Bool = false
    @State private var seizureGraphSeizureLength: Bool = false
    
    @State private var withSOZHeatmap: Bool = false
    @State private var withSOZAdminBar: Bool = false
    
    @Environment(\.presentationMode) var presentationMode
    @State private var importedFileURL: URL? = nil
    @State private var sampleSummary: String = """
    Sample summary
    2:17
    This report summarizes a 12-day long-term EEG-video monitoring study conducted on a patient...
    """
    
    var body: some View {
        ZStack {
            backgroundColor.edgesIgnoringSafeArea(.all)
            
            VStack {
                Text("Patient: \(patient.name)")
                    .font(.largeTitle)
                    .foregroundColor(.white)
                
                ScrollView {
                    renderOption(selectedTab)
                        .frame(maxWidth: .infinity, alignment: .topLeading)
                }
                .background(Color.white)
                .cornerRadius(12)
                .padding(.horizontal, 20)
                .layoutPriority(1)
                
                HStack {
                    tabButton(icon: "doc.text",
                              option: .viewFile,
                              isSelected: selectedTab == .viewFile)
                    tabButton(icon: "chart.bar",
                              option: .data,
                              isSelected: selectedTab == .data)
                    tabButton(icon: "doc.plaintext",
                              option: .summary,
                              isSelected: selectedTab == .summary)
                    tabButton(icon: "brain.head.profile",
                              option: .askQuestion,
                              isSelected: selectedTab == .askQuestion)
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
        // Trigger the API call when the view appears
        .task {
            await loadPatientDetails()
        }
    }
    
    // Example asynchronous function that fetches updated patient info from your backend
    func loadPatientDetails() async {
        // Construct the URL with the patient id (adjust the URL as needed)
        guard let url = URL(string: "https://api.example.com/patients/\(patient.id.uuidString)") else {
            print("Invalid URL")
            return
        }
        
        do {
            // Make the network call
            let (data, _) = try await URLSession.shared.data(from: url)
            // Decode the JSON data into a Patient object
            let fetchedPatient = try JSONDecoder().decode(Patient.self, from: data)
            // Update the bound patient variable on the main thread
            await MainActor.run {
                patient = fetchedPatient
            }
        } catch {
            print("Error fetching patient details: \(error)")
        }
    }
    
    // MARK: - UI components
    
    func tabButton(icon: String, option: InfoOption, isSelected: Bool) -> some View {
        Button(action: {
            selectedTab = option
        }) {
            VStack {
                Image(systemName: icon)
                    .font(.system(size: 24))
                    .foregroundColor(isSelected ? .white : backgroundColor)
                
                Text(option.title)
                    .font(.footnote)
                    .foregroundColor(isSelected ? .white : backgroundColor)
            }
            .padding()
            .background(isSelected ? backgroundColor : .white)
            .cornerRadius(10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(backgroundColor, lineWidth: 2)
            )
        }
        .frame(maxWidth: .infinity)
    }
    
    func dataTabButton(_ subOption: DataSubOption) -> some View {
        let isSelected = (selectedDataTab == subOption)
        return Button(action: {
            selectedDataTab = subOption
        }) {
            Text(subOption.title)
                .font(.footnote)
                .foregroundColor(isSelected ? .white : backgroundColor)
                .padding(.vertical, 8)
                .padding(.horizontal, 12)
                .background(isSelected ? backgroundColor : .white)
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(backgroundColor, lineWidth: 2)
                )
        }
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
        Text("Ask Question")
            .padding()
    }
    
    @ViewBuilder
    private func summaryContent() -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("EEG Monitoring Summary")
                .font(.title)
                .fontWeight(.bold)
            
            Text(sampleSummary)
                .font(.body)
                .multilineTextAlignment(.leading)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .topLeading)
    }
    
    @ViewBuilder
    private func dataContent() -> some View {
        VStack(spacing: 16) {
            Text("SEIZURE GRAPHICS")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(backgroundColor)
                .frame(maxWidth: .infinity, alignment: .center)
            
            Rectangle()
                .fill(Color.gray.opacity(0.2))
                .frame(height: 300)
                .cornerRadius(12)
                .overlay(
                    Text("Graph Placeholder")
                        .foregroundColor(.gray)
                )
            
            HStack(spacing: 12) {
                dataTabButton(.seizureGraph)
                dataTabButton(.withSOZ)
                dataTabButton(.withDrug)
            }
            .frame(maxWidth: .infinity, alignment: .center)
            
            if selectedDataTab == .seizureGraph {
                VStack(alignment: .leading, spacing: 8) {
                    Toggle("Heatmap", isOn: $seizureGraphHeatmap)
                    Toggle("Seizure length", isOn: $seizureGraphSeizureLength)
                }
                .padding(.horizontal, 20)
            }
            
            if selectedDataTab == .withSOZ {
                VStack(alignment: .leading, spacing: 8) {
                    Toggle("Heatmap", isOn: $withSOZHeatmap)
                    Toggle("Admin bar", isOn: $withSOZAdminBar)
                }
                .padding(.horizontal, 20)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .topLeading)
    }
    
    @ViewBuilder
    private func viewFileContent() -> some View {
        if let fileLocation = patient.ltmFileLocation {
            VStack(alignment: .leading, spacing: 20) {
                Text("Long Term Monitoring Report")
                    .font(.title2)
                    .padding(.bottom, 5)
                
                HStack {
                    Text(fileLocation.absoluteString)
                        .foregroundColor(.blue)
                        .underline()
                    
                    Spacer()
                    
                    Button(action: {
                        // TODO: open or share the file
                    }) {
                        Image(systemName: "arrow.up.right.square")
                            .font(.headline)
                    }
                }
            }
            .padding()
        } else {
            VStack(alignment: .leading, spacing: 20) {
                Text("No LTM Report Found")
                DocumentImporterView(importedFileURL: $importedFileURL)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .onChange(of: importedFileURL) { newValue, _ in
                        if let newValue = newValue {
                            patient.ltmFileLocation = newValue
                        }
                    }
            }
            .padding()
        }
    }
}


struct PatientView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationStack {
            PatientView(
                patient: .constant(
                    Patient(
                        name: "John Doe",
                        ltmFileLocation: nil
                    )
                )
            )
        }
    }
}
