//
//  PatientView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/14/25.
//

import SwiftUI

struct PatientView: View {
    let patient: Patient
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    @State private var selectedTab: String = "View File"
    @Environment(\.presentationMode) var presentationMode

    var body: some View {
        ZStack {
            backgroundColor.edgesIgnoringSafeArea(.all)

            VStack {
                Text("Patient: \(patient.name)")
                    .font(.largeTitle)
                    .foregroundColor(.white)
                                
                // Dynamic Content Box
                VStack {
                    Text(selectedTab)
                        .font(.title)
                        .foregroundColor(.black)
                        .padding()
                }
                .frame(maxWidth: .infinity, maxHeight: 300)
                .background(Color.white)
                .cornerRadius(12)
                .padding(.horizontal, 20)
                
                // Bottom Navigation Bar
                HStack {
                    tabButton(icon: "doc.text", text: "View File", isSelected: selectedTab == "View File")
                    tabButton(icon: "chart.bar", text: "Data", isSelected: selectedTab == "Data")
                    tabButton(icon: "doc.plaintext", text: "Summary", isSelected: selectedTab == "Summary")
                    tabButton(icon: "brain.head.profile", text: "Ask AI", isSelected: selectedTab == "Ask AI")
                }
                .padding()
                .background(Color.white)
                .clipShape(RoundedRectangle(cornerRadius: 12))
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

    // Function for bottom navigation buttons
    func tabButton(icon: String, text: String, isSelected: Bool) -> some View {
        Button(action: {
            selectedTab = text
        }) {
            VStack {
                Image(systemName: icon)
                    .font(.system(size: 24))
                    .foregroundColor(isSelected ? .blue : .gray)

                Text(text)
                    .font(.footnote)
                    .foregroundColor(isSelected ? .blue : .gray)
            }
            .padding()
        }
        .frame(maxWidth: .infinity)
    }
}

#Preview {
    NavigationStack {
        PatientView(patient: Patient(name: "John Doe", age: 40))
    }
}
