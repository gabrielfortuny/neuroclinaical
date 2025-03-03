CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name TEXT,
    dob DATE,
    created_at DATETIME DEFAULT NOW() NOT NULL,
    modified_at DATETIME DEFAULT NOW() NOT NULL
);
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    summary TEXT,
    filepath TEXT NOT NULL,
    created_at DATETIME DEFAULT NOW() NOT NULL,
    modified_at DATETIME DEFAULT NOW() NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
CREATE TABLE supplemental_materials (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    filepath TEXT NOT NULL,
    created_at DATETIME DEFAULT NOW() NOT NULL,
    modified_at DATETIME DEFAULT NOW() NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
CREATE TABLE extracted_images (
    id SERIAL PRIMARY KEY,
    report_id INT NOT NULL,
    filepath TEXT NOT NULL,
    created_at DATETIME DEFAULT NOW() NOT NULL,
    modified_at DATETIME DEFAULT NOW() NOT NULL,
    FOREIGN KEY (report_id) REFERENCES reports(id)
);