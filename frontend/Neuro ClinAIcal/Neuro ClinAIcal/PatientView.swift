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

struct PatientView: View {
    @Binding var patient: Patient
    
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    @State private var selectedTab: InfoOption = .viewFile
    @Environment(\.presentationMode) var presentationMode
    @State private var importedFileURL: URL? = nil

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
                Text(option.title)
            case .askQuestion:
                Text(option.title)
        }
    }
    
    @ViewBuilder
    private func askQuestionContent() -> some View {
        Text("Ask Question")
    }
    
    @ViewBuilder
    private func summaryContent() -> some View {
        Text("Summary")
    }
    
    @ViewBuilder
    private func dataContent() -> some View {
        Text("Data")
    }
    
    @ViewBuilder
    private func viewFileContent() -> some View {
        if let fileLocation = patient.ltmFileLocation {
            VStack(alignment: .leading, spacing: 20) {
                Text("Long Term Monitoring Report")
                    .font(.title2)
                    .padding(.bottom, 5)
                
                // A simple row that shows the file name and an icon to open or import
                HStack {
                    Text(fileLocation.absoluteString) // e.g., "Patient123LTM.pdf"
                        .foregroundColor(.blue)
                        .underline()
                        // If you want tapping this text to open the file, you can add a gesture, link, or logic.
                    
                    Spacer()
                    
                    Button(action: {
                        // TODO: Logic to open or share the file
                        print("Open file at \(fileLocation)")
                    }) {
                        Image(systemName: "arrow.up.right.square")
                            .font(.headline)
                    }
                }
            }
        } else {
            VStack(alignment: .leading, spacing: 20) {
                Text("No LTM Report Found")
//                    .font(.title2)
                DocumentImporterView(importedFileURL: $importedFileURL)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .onChange(of: importedFileURL) { newValue, _ in
                        if let newValue = newValue {
                            patient.ltmFileLocation = newValue
                        }
                    }
            }
//            .padding(.top, 20)
        }
    }
    
    var body: some View {
        ZStack {
            backgroundColor.edgesIgnoringSafeArea(.all)

            VStack {
                Text("Patient: \(patient.name)")
                    .font(.largeTitle)
                    .foregroundColor(.white)
                                
                // Dynamic Content Box
                ScrollView {
                    renderOption(selectedTab)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.white)
                .cornerRadius(12)
                .padding(.horizontal, 20)
                
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

struct PatientView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationStack {
            PatientView(
                patient: .constant(
                    Patient(
                        name: "John Doe",
                        // URL(string: "https://example.com/report.pdf")
                        ltmFileLocation: nil
                    )
                )
            )
        }
    }
}
