//
//  ContentView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/4/25.
//

import SwiftUI

struct ContentView: View {
    let patients = [
        Patient(name: "Alice", age: 45),
        Patient(name: "Bob", age: 52)
    ]
    
    @State private var expandedPatientID: UUID? = nil
    
    func patientTapped(_ patient: Patient) {
        print("\(patient.name) button tapped")
        
        if expandedPatientID == patient.id {
            expandedPatientID = nil // Collapse if already open
        } else {
            expandedPatientID = patient.id // Expand this patient and collapse others
        }
    }
    
    
    func optionButton(icon: String, text: String, color: Color, action: @escaping () -> Void) -> some View {
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
    
    func handleOptionSelection(_ option: String) {
        print("\(option) option tapped")
    }
    
    var body: some View {
        ZStack{
            Color(red: 80/255, green: 134/255, blue: 98/255).edgesIgnoringSafeArea(.all)
            VStack {
                Text("Neuro ClinAIcal")
                    .font(.largeTitle)
                    .foregroundStyle(.white)
                
                ForEach(patients) {
                    patient in Button(action: { patientTapped(patient) } ) {
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
                                optionButton(icon: "folder", text: "Manage Raw Files", color: .black) {
                                    handleOptionSelection("Manage Raw Files")
                                }
                                optionButton(icon: "arrow.up.circle", text: "Upload New Files", color: .black) {
                                    handleOptionSelection("Upload New Files")
                                }
                                optionButton(icon: "play.fill", text: "Export Data", color: .black) {
                                    handleOptionSelection("Export Data")
                                }
                                optionButton(icon: "trash", text: "Delete Patient", color: .red) {
                                    handleOptionSelection("Delete Patient")
                                }
                                
                                Button(action: { handleOptionSelection("View Patient") }) {
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
                    .frame(maxWidth: .infinity, minHeight: 50)
                    .background(Color.white)
                    .cornerRadius(10)
                    .padding(.horizontal, 20)
                }
                
                Spacer()
            }
        }
    }
}

#Preview {
    ContentView()
}
