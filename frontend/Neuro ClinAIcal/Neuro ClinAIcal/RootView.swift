//
//  RootView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/22/25.
//

import SwiftUI

struct RootView: View {
    @EnvironmentObject var session: SessionManager

    var body: some View {
        if session.currentUser == nil {
            RegistrationView(session: session)
        } else {
            MainView()
                .environmentObject(session)
        }
    }
}


//
//  RootView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/22/25.
//

//import SwiftUI
//
//struct RootView: View {
//    @EnvironmentObject var session: SessionManager
//    
//    var body: some View {
//        // 🔧 TEMP: Bypass auth and go straight to patient dashboard for testing
//        MainView()
//            .environmentObject(session)
//    }
//}

