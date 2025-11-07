-- ==========================================================
--  HOSPITAL APPOINTMENT SYSTEM DATABASE
--  Developer: Saurabh Kumar Singh
--  Roll No: BCA2225133
--  Division: B (BCA 5th Semester)
--  Project Guide: Ram Gopal Gupta
-- ==========================================================

-- Create Database
CREATE DATABASE hospital_appointment_system;
USE hospital_appointment_system;

-- ==========================================================
-- 1. USER TABLE
-- ==========================================================
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Doctor', 'Receptionist') NOT NULL
);

-- ==========================================================
-- 2. DEPARTMENT TABLE
-- ==========================================================
CREATE TABLE Department (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL
);

-- ==========================================================
-- 3. DOCTOR TABLE
-- ==========================================================
CREATE TABLE Doctor (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    department_id INT,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    contact_no VARCHAR(15),
    email VARCHAR(100),
    available_days VARCHAR(100),
    available_time VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================================================
-- 4. RECEPTIONIST TABLE
-- ==========================================================
CREATE TABLE Receptionist (
    receptionist_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    name VARCHAR(100) NOT NULL,
    contact_no VARCHAR(15),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ==========================================================
-- 5. PATIENT TABLE
-- ==========================================================
CREATE TABLE Patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    blood_group VARCHAR(10),
    contact_no VARCHAR(15),
    email VARCHAR(100),
    address VARCHAR(255),
    medical_history TEXT
);

-- ==========================================================
-- 6. APPOINTMENT TABLE
-- ==========================================================
CREATE TABLE Appointment (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    doctor_id INT,
    receptionist_id INT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    consultation_type ENUM('Online', 'In-person') DEFAULT 'In-person',
    status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    remarks TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (receptionist_id) REFERENCES Receptionist(receptionist_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- ==========================================================
-- 7. PRESCRIPTION TABLE
-- ==========================================================
CREATE TABLE Prescription (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT,
    date DATE NOT NULL,
    advice TEXT,
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ==========================================================
-- 8. MEDICINE TABLE
-- ==========================================================
CREATE TABLE Medicine (
    medicine_id INT PRIMARY KEY AUTO_INCREMENT,
    prescription_id INT,
    medicine_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50),
    duration VARCHAR(50),
    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ==========================================================
-- 9. SAMPLE DATA INSERTION
-- ==========================================================

-- Insert sample Users
INSERT INTO User (username, password, role)
VALUES 
('admin1', 'admin123', 'Admin'),
('dr_sharma', 'doc123', 'Doctor'),
('recept_sonu', 'rec123', 'Receptionist');

-- Insert Departments
INSERT INTO Department (department_name)
VALUES ('Cardiology'), ('Orthopedics'), ('Dermatology');

-- Insert Doctors
INSERT INTO Doctor (user_id, department_id, name, specialization, contact_no, email, available_days, available_time)
VALUES 
(2, 1, 'Dr. R. Sharma', 'Cardiologist', '9876543210', 'rsharma@hospital.com', 'Mon-Fri', '9AM-2PM');

-- Insert Receptionist
INSERT INTO Receptionist (user_id, name, contact_no)
VALUES (3, 'Sonu Verma', '9123456789');

-- Insert Patients
INSERT INTO Patient (name, age, gender, blood_group, contact_no, email, address, medical_history)
VALUES 
('Ravi Kumar', 34, 'Male', 'O+', '9001122334', 'ravi@gmail.com', 'Lucknow', 'None'),
('Priya Sharma', 28, 'Female', 'B+', '9998877665', 'priya@gmail.com', 'Kanpur', 'Asthma');

-- Insert Appointments
INSERT INTO Appointment (patient_id, doctor_id, receptionist_id, appointment_date, appointment_time, consultation_type, status, remarks)
VALUES 
(1, 1, 1, '2025-10-30', '10:00:00', 'In-person', 'Scheduled', 'Regular checkup'),
(2, 1, 1, '2025-10-31', '11:30:00', 'Online', 'Scheduled', 'Follow-up consultation');

-- Insert Prescription
INSERT INTO Prescription (appointment_id, date, advice)
VALUES (1, '2025-10-30', 'Continue medication and follow-up in 2 weeks');

-- Insert Medicine
INSERT INTO Medicine (prescription_id, medicine_name, dosage, duration)
VALUES 
(1, 'Aspirin', '1 tablet daily', '7 days'),
(1, 'Atorvastatin', '1 tablet nightly', '10 days');

-- ==========================================================
-- END OF SCRIPT
-- ==========================================================
Select * from Patients;
select * from doctor;
select * from User;

 SELECT d.doctor_id, d.name, d.specialization, d.contact_no, d.email, 
                   d.available_days, d.available_time, dep.department_name 
            FROM Doctor d 
            JOIN Department dep ON d.department_id = dep.department_id
            
select * from department;