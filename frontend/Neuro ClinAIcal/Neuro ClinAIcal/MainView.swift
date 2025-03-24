//
//  MainView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/4/25.
//

import SwiftUI
import UniformTypeIdentifiers

enum PatientOption {
    case export
    case delete
}

struct MainView: View {
    @EnvironmentObject var sessionManager: SessionManager
    @StateObject private var viewModel = PatientViewModel()
    
    @State private var expandedPatientID: Int? = nil
    @State private var importing = false
    @State private var showAddPatientSheet = false
    @State private var showSettings = false

    @State private var newPatientName = ""
    @State private var newPatientFileURL: URL? = nil
    
    func patientTapped(_ patient: Patient) {
        print("\(patient.name) button tapped")
        
        if expandedPatientID == patient.id {
            expandedPatientID = nil // Collapse if already open
        } else {
            expandedPatientID = patient.id // Expand this patient and collapse others
        }
    }
    
    
    func optionButton(icon: String, text: String, color: Color, action: @escaping () -> Void) -> some View { // why @escaping
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                    .font(.system(size: 20))
                
                Text(text)
                    .fontWeight(.medium)
                    .foregroundColor(color)
                
                Spacer()
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
    
    func handleOptionSelection(_ patient: Patient, _ option: PatientOption) {
        print("\(option) option tapped")
        Task {
            do {
                switch option {
                case .export:
                    print("Export Data for \(patient.name)")
                case .delete:
                    // Call async delete function:
                    try await viewModel.deletePatientServer(patientId: patient.id)
                }
                // Refresh the list after deletion.
                try await viewModel.getPatientsServer()
            } catch {
                print("Error in handleOptionSelection: \(error)")
            }
        }
    }
    
    var body: some View {
        NavigationStack {
            ZStack{
                Color(red: 80/255, green: 134/255, blue: 98/255).edgesIgnoringSafeArea(.all)
                ScrollView {
                    VStack {
                        Text("Neuro ClinAIcal")
                            .font(.largeTitle)
                            .foregroundStyle(.white)
                        
                        ForEach($viewModel.patients) {
                            $patient in Button(action: { patientTapped(patient) } ) {
                                VStack{
                                    HStack {
                                        Text(patient.name)
                                            .font(.headline)
                                            .foregroundColor(.black)
                                            .padding(.leading, 10)
                                        
                                        Spacer()
                                        
                                        Image(systemName: expandedPatientID == patient.id ? "chevron.up" : "chevron.down") // Drop-down icon
                                            .foregroundColor(.gray)
                                            .padding(.trailing, 10)
                                    }
                                    
                                    if expandedPatientID == patient.id {
                                        //                                    optionButton(icon: "folder", text: "Manage Raw Files", color: .black) {
                                        //                                        handleOptionSelection("Manage Raw Files")
                                        //                                    }
                                        //                                    optionButton(icon: "arrow.up.circle", text: "Upload New Files", color: .black) {
                                        //                                        handleOptionSelection("Upload New Files")
                                        //                                        importing = true
                                        //                                    }
                                        optionButton(icon: "play.fill", text: "Export Data", color: .black) {
                                            handleOptionSelection(patient, .export)
                                        }
                                        optionButton(icon: "trash", text: "Delete Patient", color: .red) {
                                            handleOptionSelection(patient, .delete)
                                        }
                                        
                                        NavigationLink(destination: PatientView(patient: $patient)) {
                                            Text("VIEW PATIENT")
                                                .font(.headline)
                                                .foregroundColor(.black)
                                                .padding()
                                                .frame(maxWidth: 175)
                                                .background(Color.white)
                                                .cornerRadius(8)
                                                .shadow(radius: 3)
                                        }
                                        .frame(maxWidth: .infinity, alignment: .center)
                                    }
                                }
                            }
                            .frame(maxWidth: .infinity, minHeight: expandedPatientID == patient.id ? 239 : 50)
                            .background(Color.white)
                            .cornerRadius(10)
                            .padding(.horizontal, 20)
                        }
                        
                        Button(action: {
                            showAddPatientSheet = true
                        }) {
                            Text("Add Patient")
                                .font(.headline)
                                .foregroundColor(.black)
                                .frame(maxWidth: .infinity, minHeight: 50)  // Half the height (if patient boxes are minHeight: 50)
                                .background(Color.white)
                                .cornerRadius(8)
                                .padding(.horizontal, 125)
                        }
                        .padding(.top, 10) // Positions it slightly below the patient buttons
                        
                        Spacer()
                        
                    }
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showSettings = true
                    } label: {
                        Image(systemName: "gearshape.fill")
                            .foregroundColor(.white)
                    }
                }
            }
            .sheet(isPresented: $showSettings) {
                NavigationStack {
                    SettingsView()
                        .environmentObject(sessionManager)
                        .toolbar {
                            ToolbarItem(placement: .navigationBarLeading) {
                                Button("Cancel") {
                                    showSettings = false
                                }
                            }
                        }
                }
            }
            .sheet(isPresented: $showAddPatientSheet) {
                NavigationStack {
                    VStack(alignment: .leading, spacing: 10) {
                        let titleLeading: CGFloat = 15
                        
                        Text("Patient Name:")
                            .padding(.leading, titleLeading)
                            .bold()
                        TextField("Enter patient name", text: $newPatientName)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .padding(.horizontal, 20)
                        
//                        Text("Select LTM file:")
//                            .padding(.leading, titleLeading)
//                            .bold()
//                        DocumentImporterView(importedFileURL: $newPatientFileURL)
//                            .frame(maxWidth: .infinity, alignment: .center)
                        
                        Button("Add Patient") {
                            if !newPatientName.isEmpty {
//                                viewModel.addPatient(newPatientName, newPatientFileURL)
                                Task {
                                    do {
                                        // Call the async POST function.
                                        let createdPatient = try await viewModel.createPatientServer(name: newPatientName, dob: nil)
                                        // Optionally, refresh the patient list.
                                        try await viewModel.getPatientsServer()
                                        newPatientName = ""
                                        showAddPatientSheet = false
                                    } catch {
                                        print("Error creating patient: \(error)")
                                    }
                                }
                            }
                        }
                            .frame(maxWidth: .infinity, alignment: .center)
                            .padding()
                        
                        Spacer()
                    }
                    .navigationTitle("Add Patient Form")
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .navigationBarLeading) {
                            Button("Cancel") {
                                showAddPatientSheet = false
                            }
                        }
                    }
                }
            }
        }
        .task {
            do {
                try await viewModel.getPatientsServer()
            } catch {
                print("Error fetching patients: \(error)")
            }
        }
    }
}

struct MainView_Previews: PreviewProvider {
    static var previews: some View {
        let session = SessionManager()
        session.logIn(email: "Demo@example.com", password: "123")
        return NavigationStack {
            MainView()
                .environmentObject(session)
        }
    }
}
