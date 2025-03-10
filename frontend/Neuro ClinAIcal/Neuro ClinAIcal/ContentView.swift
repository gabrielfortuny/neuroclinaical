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
    
    func patientTapped(_ patient: Patient) {
        print("\(patient.name) button tapped")
    }
    
    var body: some View {
        ZStack{
            Color(red: 80/255, green: 134/255, blue: 98/255).edgesIgnoringSafeArea(.all)
            VStack {
                Text("Neuro ClinAIcal")
                    .font(.largeTitle)
                    .foregroundStyle(.white)
                
                ForEach(patients) { patient in Button(action: { patientTapped(patient) }) {
                        HStack {
                            Spacer() // Pushes text to center
                            
                            Text(patient.name)
                                .font(.headline)
                                .foregroundColor(.black)
                            
                            Spacer() // Pushes icon to the right
                            
                            Image(systemName: "chevron.down") // Drop-down icon
                                .foregroundColor(.gray)
                                .padding(.trailing, 15)
                        }
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(Color.white)
                        .cornerRadius(10)
                        .padding(.horizontal, 20)
                    }
                }
                
                Spacer()
            }
        }
    }
}

#Preview {
    ContentView()
}
