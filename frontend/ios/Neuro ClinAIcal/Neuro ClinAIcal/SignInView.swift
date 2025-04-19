//
//  SignInView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/9/25.
//

import SwiftUI

struct SignInView: View {
    @EnvironmentObject var session: SessionManager
    
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var isPasswordVisible: Bool = false
    @State private var showError: Bool = false

    var body: some View {
        if session.currentUser != nil {
            MainView()
                .environmentObject(session)
        } else {
            ZStack {
                Color(red: 80/255, green: 134/255, blue: 98/255)
                    .edgesIgnoringSafeArea(.all)
                
                VStack {
                    Text("Sign In")
                        .font(.largeTitle)
                        .foregroundColor(.white)
                        .padding(.bottom, 30)
                        .padding(.top, 30)
                    
                    // Email Field
                    TextField("Email", text: $email)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(10)
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)
                        .padding(.horizontal, 20)
                    
                    // Password Field with Toggle Visibility
                    HStack {
                        if isPasswordVisible {
                            TextField("Password", text: $password)
                        } else {
                            SecureField("Password", text: $password)
                        }
                        
                        Button(action: {
                            isPasswordVisible.toggle()
                        }) {
                            Image(systemName: isPasswordVisible ? "eye.slash" : "eye")
                                .foregroundColor(.gray)
                        }
                        .padding(.trailing, 10)
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(10)
                    .padding(.horizontal, 20)
                    
                    // Sign In Button
                    Button(action: {
                        session.logIn(email: email, password: password)
                    }) {
                        Text("Sign In")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                            .padding(.horizontal, 20)
                    }
                    .padding(.top, 20)
                    
                    // Error Message (if credentials are incorrect)
                    if showError {
                        Text("Invalid email or password")
                            .foregroundColor(.red)
                            .padding(.top, 10)
                    }
                    
                    Button(action: {
                        session.logIn(email: "Demo@example.com", password: "123")
                    }) {
                        Text("Demo")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                            .padding(.horizontal, 20)
                    }
                    
                    Spacer()
                }
            }
        }
    }
}
