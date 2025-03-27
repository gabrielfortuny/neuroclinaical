import SwiftUI

struct RegistrationView: View {
    @EnvironmentObject var session: SessionManager
    @StateObject private var viewModel: RegistrationViewModel

    
    init(session: SessionManager) {
        _viewModel = StateObject(wrappedValue: RegistrationViewModel(session: session))
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("Register")
                    .font(.largeTitle)
                    .bold()
                
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
                
                if let errorMessage = viewModel.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                }
                
                Button(action: {
                    viewModel.register()
                }) {
                    if viewModel.isLoading {
                        ProgressView()
                    } else {
                        Text("Register")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .disabled(viewModel.isLoading)
                
                Spacer()
            }
            .padding()
            .navigationTitle("User Registration")
            .alert(isPresented: $viewModel.showSuccess) {
                Alert(title: Text("Success"),
                      message: Text("Registration successful!"),
                      dismissButton: .default(Text("OK")))
            }
        }
    }
}

struct RegistrationView_Previews: PreviewProvider {
    static var previews: some View {
        RegistrationView(session: SessionManager())
    }
}
