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
    @EnvironmentObject var session: SessionManager
    @Binding var patient: Patient
    
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    @State private var selectedTab: InfoOption = .viewFile
    @Environment(\.presentationMode) var presentationMode
    @State private var importedFileURL: URL? = nil
    @State private var expandedSessionID: UUID? = nil
    
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
    
    @ViewBuilder
    private func viewFileContent() -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                ForEach(Array(patient.sessions.enumerated()), id: \.element.id) { index, session in
                    Button(action: {
                        if expandedSessionID == session.id {
                            expandedSessionID = nil
                        } else {
                            expandedSessionID = session.id
                        }
                    }) {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Session \(index + 1)")
                                .foregroundColor(.black)
                            if expandedSessionID == session.id {
                                Button("Delete Session") {
                                    patient.deleteSession(withId: session.id)
                                }
                                .font(.caption)
                                .foregroundColor(.red)
                                .padding(5)
                                .background(Color.gray.opacity(0.2))
                                .cornerRadius(5)
                            }
                        }
                        .padding()
                    }
                    .frame(maxWidth: .infinity, minHeight: 50)
                    .background(Color.white)
                    .cornerRadius(8)
                }
                
                Button(action: {
                    patient.sessions.append(Session())
                }) {
                    Text("Add Session")
                        .font(.headline)
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(Color.white)
                        .cornerRadius(8)
                }
            }
            .padding(.horizontal, 20)
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
                
                Spacer()
                                
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

struct PatientView_Previews: PreviewProvider {
    static var previews: some View {
        let session = SessionManager()
        session.logIn(email: "Demo@example.com", password: "123")
        return NavigationStack {
            PatientView(
                patient: .constant(
                    Patient(
                        name: "John Doe"
                    )
                )
            )
            .environmentObject(session)
        }
    }
}
