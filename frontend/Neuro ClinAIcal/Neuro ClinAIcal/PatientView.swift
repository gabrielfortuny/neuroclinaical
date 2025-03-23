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
                Text(option.title)
            case .summary:
                Text(option.title)
            case .askQuestion:
                Text(option.title)
        }
    }
    
    @ViewBuilder
    private func viewFileContent() -> some View {
        if let fileLocation = patient.ltmFileLocation {
            // We have a file location -> Show LTM
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
                .padding(.horizontal)
            }
            .padding(.top, 20)
        } else {
            // No file -> Prompt user to import
            VStack(alignment: .leading, spacing: 20) {
                Text("No LTM Report Found")
                    .font(.title2)
                
                Text("Would you like to import a Long Term Monitoring Report for this patient?")
                    .foregroundColor(.gray)
                
                Button("Import File") {
                    // TODO: Trigger your file importer logic
                    print("Trigger file import for \(patient.name)")
                }
                .font(.headline)
                .padding()
                .background(Color.blue.opacity(0.2))
                .cornerRadius(8)
            }
            .padding(.top, 20)
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
                    VStack {
                        renderOption(selectedTab)
                    }
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
