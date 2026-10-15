-- AI Medical Imaging Analysis System
-- Database Setup Script
-- BBIS 7502 Applied Project — ICL Graduate Business School
-- Student: Saroj Kumar Tamang | Student ID: 108579

-- Step 1: Create the database
CREATE DATABASE medical_imaging_db;

-- Step 2: Select the database
USE medical_imaging_db;

-- Step 3: Create users table for Google OAuth multi-user support
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Create analysis history table linked to users
CREATE TABLE analysis_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image_name VARCHAR(255) NOT NULL,
    image_modality VARCHAR(200),
    full_report TEXT,
    is_urgent BOOLEAN DEFAULT FALSE,
    analysed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Step 5: Verify tables created
SHOW TABLES;