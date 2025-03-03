-- https://lucid.app/lucidchart/a8b4be3b-ccad-4e50-8a5e-e9f78e4d78cc/edit?invitationId=inv_4caef618-5598-4fea-ad12-e5acb15c6430
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL
);
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name TEXT,
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
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
CREATE TABLE supplemental_materials (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    filepath TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
CREATE TABLE extracted_images (
    id SERIAL PRIMARY KEY,
    report_id INT NOT NULL,
    filepath TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    modified_at TIMESTAMP DEFAULT NOW() NOT NULL,
    FOREIGN KEY (report_id) REFERENCES reports(id)
);