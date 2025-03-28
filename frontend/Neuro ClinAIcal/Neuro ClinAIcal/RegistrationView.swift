import SwiftUI

struct RegistrationView: View {
    @EnvironmentObject var session: SessionManager
    @StateObject private var viewModel: RegistrationViewModel
    
    // Custom initializer to inject SessionManager
    init(session: SessionManager) {
        _viewModel = StateObject(wrappedValue: RegistrationViewModel(session: session))
    }
    
    var body: some View {
        ZStack {
            // 1) Green background
            Color(red: 80/255, green: 134/255, blue: 98/255)
                .edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 24) {
                // 2) White Title
                Text("Patient Portal")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .padding(.top, 40)
                
                // 3) White Card for registration form
                VStack(spacing: 16) {
                    
                    Text("Register")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.black)
                    
                    TextField("Username", text: $viewModel.username)
                        .autocapitalization(.none)
                        .padding()
                        .background(Color(UIColor.systemGray6))
                        .cornerRadius(8)
                    
                    TextField("Email", text: $viewModel.email)
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)
                        .padding()
                        .background(Color(UIColor.systemGray6))
                        .cornerRadius(8)
                    
                    SecureField("Password", text: $viewModel.password)
                        .textContentType(.newPassword)
                        .padding()
                        .background(Color(UIColor.systemGray6))
                        .cornerRadius(8)
                    
                    SecureField("Confirm Password", text: $viewModel.confirmPassword)
                        .textContentType(.newPassword)
                        .padding()
                        .background(Color(UIColor.systemGray6))
                        .cornerRadius(8)
                    
                    // Error message
                    if let errorMessage = viewModel.errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                    }
                    
                    // 4) Register button
                    Button {
                        viewModel.register()
                    } label: {
                        if viewModel.isLoading {
                            ProgressView()
                        } else {
                            Text("Register")
                                .font(.headline)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(8)
                        }
                    }
                    .disabled(viewModel.isLoading)
                }
                .padding(20)
                .background(Color.white)
                .cornerRadius(12)
                .shadow(radius: 5)
                .padding(.horizontal, 30)
                
                Spacer()
            }
            .alert(isPresented: $viewModel.showSuccess) {
                Alert(title: Text("Success"),
                      message: Text("Registration successful!"),
                      dismissButton: .default(Text("OK")))
            }
        }
        .navigationBarBackButtonHidden(true)
        .navigationBarHidden(true)
    }
}

// For SwiftUI previews only:
struct RegistrationView_Previews: PreviewProvider {
    static var previews: some View {
        RegistrationView(session: SessionManager())
            .environmentObject(SessionManager())
    }
}
