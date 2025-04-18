//
//  PatientView.swift
//  Neuro ClinAIcal
//
//  Created by Adam Nehme on 3/14/25.
//

import SwiftUI
import UniformTypeIdentifiers
import Charts

// MARK: - Models for Graph Data

struct DrugData: Codable, Identifiable {
    let id: Int
    let drugName: String
    let drugClass: String? // Optional if backend sends null
    let day: Int
    let dosage: Int
    let time: String?      // Optional if backend sends null

    enum CodingKeys: String, CodingKey {
        case id
        case drugName = "drug_name"
        case drugClass = "drug_class"
        case day
        case dosage
        case time
    }
}

struct SeizureData: Identifiable, Decodable {
    let id: Int
    let day: Int
    let seizureTime: String?
    let duration: Double
    let createdAt: String?
    let modifiedAt: String?
    let electrodes: [String]

    private enum CodingKeys: String, CodingKey {
        case id, day, duration, electrodes
        case seizureTime = "seizure_time"
        case createdAt = "created_at"
        case modifiedAt = "modified_at"
    }
}

struct GraphDataResponse: Decodable {
    let drugs: [DrugData]
    let seizures: [SeizureData]
}

// Helper model for grouping seizure counts by day (只定义一次)
struct SeizureDayGroup: Identifiable {
    let id: Int
    let day: Int
    let count: Int
}

struct SeizureBarChartView: View {
    let data: [SeizureDayGroup]
    
    var body: some View {
        Chart {
            ForEach(data) { group in
                BarMark(
                    x: .value("Day", group.day),
                    y: .value("Seizure Count", group.count)
                )
                .foregroundStyle(.blue)
            }
        }
        .chartXAxis {
            AxisMarks(values: .automatic) { _ in
                AxisGridLine()
                AxisTick()
                AxisValueLabel()
            }
        }
        .chartYAxis {
            AxisMarks() { _ in
                AxisGridLine()
                AxisTick()
                AxisValueLabel()
            }
        }
        .padding()
    }
}

// MARK: - Enums for PatientView Tabs and File Types

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

enum FileType: Equatable {
    case report
    case supplemental
}


struct PatientView: View {
    @EnvironmentObject private var sessionManager: SessionManager
    var patient: Patient
    
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    @State private var selectedTab: InfoOption = .viewFile
    @Environment(\.presentationMode) var presentationMode
    
    // File importer states
    @State private var importedReportURL: URL? = nil
    @State private var importedSupplementalURL: URL? = nil
    var allowedTypes: [UTType] {
        var types: [UTType] = [.pdf]
        if let docType = UTType("com.microsoft.word.doc") { types.append(docType) }
        if let docxType = UTType("org.openxmlformats.wordprocessingml.document") { types.append(docxType) }
        return types
    }
    
    // Graph data states for "Data" tab
    @State private var seizureData: [SeizureData] = []
    @State private var drugData: [DrugData] = []
    @State private var isLoadingGraphData = false
    @State private var graphDataError: String? = nil
    
    // Asynchronous function to fetch graph data (JSON) from the backend
    func fetchGraphData(for patientId: Int) async {
        isLoadingGraphData = true
        defer { isLoadingGraphData = false }
        
        // Replace with your server's URL
        guard let url = URL(string: "http://10.0.0.173:8000/patients/\(patientId)/graphData") else {
            graphDataError = "Invalid URL"
            return
        }
        
        do {
            let (data, response) = try await URLSession.shared.data(from: url)
            guard (response as? HTTPURLResponse)?.statusCode == 200 else {
                graphDataError = "Bad response from server"
                return
            }
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            let graphResponse = try decoder.decode(GraphDataResponse.self, from: data)
            print("✅ Decoded seizures:", graphResponse.seizures)
            print("✅ Decoded drugs:", graphResponse.drugs)

            self.drugData = graphResponse.drugs
            self.seizureData = graphResponse.seizures
        } catch {
            graphDataError = error.localizedDescription
            print("Error fetching graph data: \(error)")
        }
    }
    
    // Bottom tab button
    func tabButton(icon: String, option: InfoOption, isSelected: Bool) -> some View {
        Button(action: { selectedTab = option }) {
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
    
    // Render the selected tab's content
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
    
    private func askQuestionContent() -> some View {
        ScrollView {
            Text("Ask Question MVP")
        }
    }
    
    private func summaryContent() -> some View {
        ScrollView {
            Text("Summary")
        }
    }
    
    // Data content: displays graph data using Swift Charts and fetches JSON via async/await.
    private func dataContent() -> some View {
        ScrollView {
            VStack(spacing: 16) {
                Text("SEIZURE GRAPHICS")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(backgroundColor)
                    .frame(maxWidth: .infinity, alignment: .center)
                
                if isLoadingGraphData {
                    ProgressView("Loading Graph Data...")
                } else if let error = graphDataError {
                    Text("Error: \(error)")
                        .foregroundColor(.red)
                } else {
                    Chart {
                        // Group seizures by day and show a simple count using BarMark.
                        ForEach(groupSeizuresByDay()) { group in
                            BarMark(
                                x: .value("Day", group.day),
                                y: .value("Seizure Count", group.count)
                            )
                            .foregroundStyle(.blue)
                        }
                    }
                    .frame(height: 200)
                    .padding(.horizontal)
                }
                
                // Example Toggles – replace with your actual state variables as needed.
                Toggle("Seizure Length", isOn: .constant(false))
                Toggle("Drug Administration", isOn: .constant(false))
            }
            .padding()
        }
        .task {
            await fetchGraphData(for: patient.id)
        }
    }
    
    // Helper to group seizures by day for the chart.
    private func groupSeizuresByDay() -> [SeizureDayGroup] {
        var counts: [Int: Int] = [:]
        for seizure in seizureData {
            counts[seizure.day, default: 0] += 1
        }
        return counts.map { SeizureDayGroup(id: $0.key, day: $0.key, count: $0.value) }
            .sorted { $0.day < $1.day }
    }
    
    // Basic file viewing content for demonstration.
    private func viewFileContent() -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Long Term Monitoring Report")
                    .font(.title2)
                    .padding(.bottom, 5)
                // Replace with your file display logic
                Text("File content will be shown here...")
            }
            .padding()
        }
    }
    
    var body: some View {
        ZStack {
            backgroundColor.edgesIgnoringSafeArea(.all)
            VStack {
                Text("Patient: \(patient.name)")
                    .font(.largeTitle)
                    .foregroundColor(.white)
                
                // Updated chart view call –直接使用 groupSeizuresByDay()
                SeizureBarChartView(data: groupSeizuresByDay())
                    .frame(height: 300)
                
                renderOption(selectedTab)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.white)
                    .cornerRadius(12)
                    .padding(.horizontal)
                
                // Bottom Navigation Bar
                HStack {
                    tabButton(icon: "doc.text", option: .viewFile, isSelected: selectedTab == .viewFile)
                    tabButton(icon: "chart.bar", option: .data, isSelected: selectedTab == .data)
                    tabButton(icon: "doc.plaintext", option: .summary, isSelected: selectedTab == .summary)
                    tabButton(icon: "brain.head.profile", option: .askQuestion, isSelected: selectedTab == .askQuestion)
                }
                .padding(.horizontal, 10)
            }
        }
        .navigationBarBackButtonHidden(true)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button {
                    presentationMode.wrappedValue.dismiss()
                } label: {
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

// MARK: - Preview

struct PatientView_Previews: PreviewProvider {
    static var previews: some View {
        let session = SessionManager()
        session.logIn(email: "Demo@example.com", password: "123")
        let patient = Patient(id: 1, name: "John Doe")
        return NavigationStack {
            PatientView(patient: patient)
                .environmentObject(session)
        }
    }
}
