-- https://lucid.app/lucidchart/a8b4be3b-ccad-4e50-8a5e-e9f78e4d78cc/edit?invitationId=inv_4caef618-5598-4fea-ad12-e5acb15c6430
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL
);
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    dob DATE,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL
);
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    summary TEXT,
    filepath TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
CREATE TABLE extracted_images (
    id SERIAL PRIMARY KEY,
    report_id INT NOT NULL,
    filepath TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);
CREATE TABLE supplemental_materials (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    filepath TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
CREATE TABLE seizures (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    day INT NOT NULL,
    start_time TIME,
    duration INTERVAL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
CREATE TABLE electrodes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL
);
CREATE TABLE seizures_electrodes (
    seizure_id INT,
    electrode_id INT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL,
    PRIMARY KEY (seizure_id, electrode_id),
    FOREIGN KEY (seizure_id) REFERENCES seizures(id) ON DELETE CASCADE,
    FOREIGN KEY (electrode_id) REFERENCES electrodes(id) ON DELETE CASCADE
);
CREATE TABLE drugs (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    class TEXT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL
);
CREATE TABLE drug_administration (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    drug_id INT NOT NULL,
    day INT NOT NULL,
    dosage INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (drug_id) REFERENCES drugs(id) ON DELETE CASCADE
);
CREATE INDEX idx_seizures_patient_id ON seizures(patient_id);
CREATE INDEX idx_drug_administration_patient_id ON drug_administration(patient_id);
CREATE INDEX idx_drug_administration_drug_id ON drug_administration(drug_id);
CREATE INDEX idx_seizure_electrodes_seizure_id ON seizure_electrodes(seizure_id);
CREATE INDEX idx_seizure_electrodes_electrode_id ON seizure_electrodes(electrode_id);