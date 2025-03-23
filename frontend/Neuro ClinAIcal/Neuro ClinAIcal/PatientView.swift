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
    @Binding var patient: Patient
    
    let backgroundColor = Color(red: 80/255, green: 134/255, blue: 98/255)
    @State private var selectedTab: InfoOption = .viewFile
    @Environment(\.presentationMode) var presentationMode
    @State private var importedFileURL: URL? = nil
    @State private var sampleSummary: String = """
    Sample summary
    2:17
    This report summarizes a 12-day long-term EEG-video monitoring study conducted on a patient with medically-refractory post-traumatic epilepsy and migraine headaches. The patient underwent the placement of 16 bilateral ROSA-guided depth electrodes for stereoEEG testing to localize seizure activity in anticipation of potential epilepsy surgery, likely neuromodulation. The study aimed to characterize the patient's clinical events and interictal epileptiform discharges (IEDs).

    ### Key Findings:
    1. **Electrode Placement and Targets**:
    Electrodes were placed in various brain regions, including the amygdala, hippocampus (anterior, middle, posterior), cingulate, insula, and SPECT-related areas. The right hemisphere was more extensively monitored.
    2. **Medication Adjustments**:
    The patient was on multiple neuroactive medications, including Xcopri, Zonisamide, and others. Medications were adjusted during the monitoring period, with Zonisamide and Cenobamate being tapered off and later restarted.
    3. **Interictal EEG Findings**:
    - Frequent spikes and sharp waves were observed, particularly in the right middle hippocampus (RMH 1-2), with fields extending to other regions like the right anterior hippocampus (RAH) and right posterior hippocampus (RPH).
    - Independent spikes were also noted in the left middle hippocampus (LMH) and left amygdala (LAM).
    - Scalp EEG showed a symmetric, well-modulated posterior background rhythm with no focal or epileptiform abnormalities.
    4. **Ictal EEG Findings**:
    - **Subclinical Seizures**:
        - Type 1: Rhythmic spikes starting at RMH 1-2, propagating to RAH 1-2, increasing to 1 Hz.
        - Type 2: Evolved into faster frequency spikes (up to 8 Hz).
        - Type 3: Low-amplitude spike-wave discharges at RAH 1-2 and RMH 1-2.
    - **Clinical Seizures**:
        - Type 1: Onset at RMH 1-2, with nausea, vomiting, aphasia.
        - Type 2: Same onset with fear and inability to speak.
    5. **Seizure Localization**:
    - Interictal findings suggest RMH 1-2 is within the epileptogenic zone.
    - Ictal onset localized to RMH 1-2, though not clearly distinct from interictal discharges.
    6. **Clinical Correlation**:
    - Seizures with vomiting and aphasia align with right mesial temporal localization.
    7. **Final Diagnosis**:
    - Focal symptomatic epilepsy with complex partial seizures, intractable, with status epilepticus.

    ### Conclusion:
    The 12-day monitoring localized the epileptogenic zone to RMH 1-2. This supports treatment decisions such as surgery or neuromodulation. Reviewed by attending physicians.
    """


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
                Text(option.title)
            case .summary:
                SummaryView(title: "PATIENT 123", summaryText: sampleSummary)
            case .askQuestion:
                Text(option.title)
        }
    }
    
    @ViewBuilder
    private func askQuestionContent() -> some View {
        Text("Ask Question")
    }
    
    @ViewBuilder
    private func summaryContent() -> some View {
        Text("Summary")
    }
    
    @ViewBuilder
    private func dataContent() -> some View {
        Text("Data")
    }
    
    @ViewBuilder
    private func viewFileContent() -> some View {
        if let fileLocation = patient.ltmFileLocation {
            VStack(alignment: .leading, spacing: 20) {
                Text("Long Term Monitoring Report")
                    .font(.title2)
                    .padding(.bottom, 5)
                
                // A simple row that shows the file name and an icon to open or import
                HStack {
                    Text(fileLocation.absoluteString) // e.g., "Patient123LTM.pdf"
                        .foregroundColor(.blue)
                        .underline()
                        // If you want tapping this text to open the file, you can add a gesture, link, or logic.
                    
                    Spacer()
                    
                    Button(action: {
                        // TODO: Logic to open or share the file
                        print("Open file at \(fileLocation)")
                    }) {
                        Image(systemName: "arrow.up.right.square")
                            .font(.headline)
                    }
                }
            }
        } else {
            VStack(alignment: .leading, spacing: 20) {
                Text("No LTM Report Found")
//                    .font(.title2)
                DocumentImporterView(importedFileURL: $importedFileURL)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .onChange(of: importedFileURL) { newValue, _ in
                        if let newValue = newValue {
                            patient.ltmFileLocation = newValue
                        }
                    }
            }
//            .padding(.top, 20)
        }
    }
    
    var body: some View {
        ZStack {
            backgroundColor.edgesIgnoringSafeArea(.all)

            VStack {
                Text("Patient: \(patient.name)")
                    .font(.largeTitle)
                    .foregroundColor(.white)
                                
                // Dynamic Content Box
                ScrollView {
                    renderOption(selectedTab)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.white)
                .cornerRadius(12)
                .padding(.horizontal, 20)
                
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
        NavigationStack {
            PatientView(
                patient: .constant(
                    Patient(
                        name: "John Doe",
                        // URL(string: "https://example.com/report.pdf")
                        ltmFileLocation: nil
                    )
                )
            )
        }
    }
}


struct SummaryView: View {
    let title: String
    let summaryText: String

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(title)
                    .font(.title)
                    .fontWeight(.bold)

                Text(summaryText)
                    .font(.body)
                    .multilineTextAlignment(.leading)
            }
            .padding()
        }
    }
}
