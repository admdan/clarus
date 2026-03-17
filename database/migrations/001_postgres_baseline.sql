-- Baseline PostgreSQL schema for Clarus / itflask.
-- This migration is intentionally idempotent so it can repair partially-migrated
-- local databases that were previously switched from MySQL.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'basic',
    profile_picture TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'basic';
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    recipient_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    target_role VARCHAR(50),
    message TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE notifications ADD COLUMN IF NOT EXISTS sender_id INTEGER;
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS recipient_id INTEGER;
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS target_role VARCHAR(50);
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS message TEXT;
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS assets (
    asset_id SERIAL PRIMARY KEY,
    device_type VARCHAR(100) NOT NULL,
    serial_number VARCHAR(255) NOT NULL,
    "condition" VARCHAR(100) NOT NULL,
    status VARCHAR(100) NOT NULL,
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    date_assigned TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    added_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    model VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    purchase_date DATE NOT NULL,
    warranty_end DATE,
    location VARCHAR(255),
    ip_mac VARCHAR(255),
    asset_tag VARCHAR(255),
    invoice_ref VARCHAR(255),
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE assets ADD COLUMN IF NOT EXISTS device_type VARCHAR(100);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS serial_number VARCHAR(255);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS "condition" VARCHAR(100);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS status VARCHAR(100);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS assigned_to INTEGER;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS date_assigned TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS remarks TEXT;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS added_by INTEGER;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS model VARCHAR(255);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(255);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS purchase_date DATE;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS warranty_end DATE;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS location VARCHAR(255);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS ip_mac VARCHAR(255);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS asset_tag VARCHAR(255);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS invoice_ref VARCHAR(255);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS export_logs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    export_type VARCHAR(50) NOT NULL,
    is_single_asset SMALLINT NOT NULL DEFAULT 0,
    filters_applied TEXT,
    exported_asset_ids TEXT,
    num_assets INTEGER NOT NULL DEFAULT 0,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE export_logs ADD COLUMN IF NOT EXISTS filename VARCHAR(255);
ALTER TABLE export_logs ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE export_logs ADD COLUMN IF NOT EXISTS export_type VARCHAR(50);
ALTER TABLE export_logs ADD COLUMN IF NOT EXISTS is_single_asset SMALLINT DEFAULT 0;
ALTER TABLE export_logs ADD COLUMN IF NOT EXISTS filters_applied TEXT;
ALTER TABLE export_logs ADD COLUMN IF NOT EXISTS exported_asset_ids TEXT;
ALTER TABLE export_logs ADD COLUMN IF NOT EXISTS num_assets INTEGER DEFAULT 0;
ALTER TABLE export_logs ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS change_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    field_requested VARCHAR(255) NOT NULL,
    new_value TEXT,
    note TEXT,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    resolved_at TIMESTAMP WITHOUT TIME ZONE,
    admin_note TEXT,
    resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS field_requested VARCHAR(255);
ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS new_value TEXT;
ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS note TEXT;
ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'Pending';
ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS admin_note TEXT;
ALTER TABLE change_requests ADD COLUMN IF NOT EXISTS resolved_by INTEGER;

CREATE TABLE IF NOT EXISTS user_profile (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255),
    date_of_birth DATE,
    gender VARCHAR(50),
    contact_number VARCHAR(100),
    address TEXT,
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS gender VARCHAR(50);
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS contact_number VARCHAR(100);
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_pii (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    id_type VARCHAR(100),
    id_number VARCHAR(255),
    citizenship VARCHAR(100),
    emergency_contact_name VARCHAR(255),
    emergency_contact_number VARCHAR(100),
    emergency_contact_address TEXT,
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_pii ADD COLUMN IF NOT EXISTS id_type VARCHAR(100);
ALTER TABLE user_pii ADD COLUMN IF NOT EXISTS id_number VARCHAR(255);
ALTER TABLE user_pii ADD COLUMN IF NOT EXISTS citizenship VARCHAR(100);
ALTER TABLE user_pii ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(255);
ALTER TABLE user_pii ADD COLUMN IF NOT EXISTS emergency_contact_number VARCHAR(100);
ALTER TABLE user_pii ADD COLUMN IF NOT EXISTS emergency_contact_address TEXT;
ALTER TABLE user_pii ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_employment (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    job_title VARCHAR(255),
    department VARCHAR(255),
    work_email VARCHAR(255),
    date_joined DATE,
    employment_status VARCHAR(100),
    supervisor VARCHAR(255),
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_employment ADD COLUMN IF NOT EXISTS job_title VARCHAR(255);
ALTER TABLE user_employment ADD COLUMN IF NOT EXISTS department VARCHAR(255);
ALTER TABLE user_employment ADD COLUMN IF NOT EXISTS work_email VARCHAR(255);
ALTER TABLE user_employment ADD COLUMN IF NOT EXISTS date_joined DATE;
ALTER TABLE user_employment ADD COLUMN IF NOT EXISTS employment_status VARCHAR(100);
ALTER TABLE user_employment ADD COLUMN IF NOT EXISTS supervisor VARCHAR(255);
ALTER TABLE user_employment ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_banking (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    bank_name VARCHAR(255),
    bank_account_number VARCHAR(255),
    account_holder_name VARCHAR(255),
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_banking ADD COLUMN IF NOT EXISTS bank_name VARCHAR(255);
ALTER TABLE user_banking ADD COLUMN IF NOT EXISTS bank_account_number VARCHAR(255);
ALTER TABLE user_banking ADD COLUMN IF NOT EXISTS account_holder_name VARCHAR(255);
ALTER TABLE user_banking ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_family (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    marital_status VARCHAR(100),
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_family ADD COLUMN IF NOT EXISTS marital_status VARCHAR(100);
ALTER TABLE user_family ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_spouses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    spouse_name VARCHAR(255),
    spouse_id_type VARCHAR(100),
    spouse_id_number VARCHAR(255),
    spouse_address TEXT,
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_spouses ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE user_spouses ADD COLUMN IF NOT EXISTS spouse_name VARCHAR(255);
ALTER TABLE user_spouses ADD COLUMN IF NOT EXISTS spouse_id_type VARCHAR(100);
ALTER TABLE user_spouses ADD COLUMN IF NOT EXISTS spouse_id_number VARCHAR(255);
ALTER TABLE user_spouses ADD COLUMN IF NOT EXISTS spouse_address TEXT;
ALTER TABLE user_spouses ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_dependents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dependent_name VARCHAR(255),
    dependent_relationship VARCHAR(100),
    dependent_birthdate DATE,
    dependent_notes TEXT,
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_dependents ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE user_dependents ADD COLUMN IF NOT EXISTS dependent_name VARCHAR(255);
ALTER TABLE user_dependents ADD COLUMN IF NOT EXISTS dependent_relationship VARCHAR(100);
ALTER TABLE user_dependents ADD COLUMN IF NOT EXISTS dependent_birthdate DATE;
ALTER TABLE user_dependents ADD COLUMN IF NOT EXISTS dependent_notes TEXT;
ALTER TABLE user_dependents ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_vehicles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(100),
    make VARCHAR(255),
    model VARCHAR(255),
    year_model VARCHAR(50),
    plate_number VARCHAR(100),
    color VARCHAR(100),
    parking_permit_id VARCHAR(100),
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS vehicle_type VARCHAR(100);
ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS make VARCHAR(255);
ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS model VARCHAR(255);
ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS year_model VARCHAR(50);
ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS plate_number VARCHAR(100);
ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS color VARCHAR(100);
ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS parking_permit_id VARCHAR(100);
ALTER TABLE user_vehicles ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    file_path TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    display_name VARCHAR(255),
    uploaded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_documents ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE user_documents ADD COLUMN IF NOT EXISTS document_type VARCHAR(100);
ALTER TABLE user_documents ADD COLUMN IF NOT EXISTS file_path TEXT;
ALTER TABLE user_documents ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'Pending';
ALTER TABLE user_documents ADD COLUMN IF NOT EXISTS display_name VARCHAR(255);
ALTER TABLE user_documents ADD COLUMN IF NOT EXISTS uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS devices (
    device_id SERIAL PRIMARY KEY,
    device_type VARCHAR(100),
    device_code VARCHAR(100),
    hostname VARCHAR(255),
    ipv4_addresses TEXT,
    ipv6_addresses TEXT,
    mac_addresses TEXT,
    network_adapters TEXT,
    os_name VARCHAR(255),
    os_version VARCHAR(255),
    manufacturer VARCHAR(255),
    device_model VARCHAR(255),
    serial_number VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE devices ADD COLUMN IF NOT EXISTS device_type VARCHAR(100);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS device_code VARCHAR(100);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS hostname VARCHAR(255);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS ipv4_addresses TEXT;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS ipv6_addresses TEXT;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS mac_addresses TEXT;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS network_adapters TEXT;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS os_name VARCHAR(255);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS os_version VARCHAR(255);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(255);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS device_model VARCHAR(255);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS serial_number VARCHAR(255);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    device_id INTEGER REFERENCES devices(device_id) ON DELETE SET NULL,
    device_type VARCHAR(100),
    issue_description TEXT NOT NULL,
    troubleshooting TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Open',
    date_reported TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    priority VARCHAR(50),
    category VARCHAR(100),
    assigned_to VARCHAR(255),
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE tickets ADD COLUMN IF NOT EXISTS user_name VARCHAR(255);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS device_id INTEGER;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS device_type VARCHAR(100);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS issue_description TEXT;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS troubleshooting TEXT;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'Open';
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS date_reported TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS due_date DATE;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS priority VARCHAR(50);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS category VARCHAR(100);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(255);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);

CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_recipient_id ON notifications (recipient_id);
CREATE INDEX IF NOT EXISTS idx_notifications_target_role ON notifications (target_role);

CREATE INDEX IF NOT EXISTS idx_assets_assigned_to ON assets (assigned_to);
CREATE INDEX IF NOT EXISTS idx_assets_device_type ON assets (device_type);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets (status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_assets_serial_number ON assets (serial_number);

CREATE INDEX IF NOT EXISTS idx_export_logs_user_id ON export_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_export_logs_timestamp ON export_logs (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_change_requests_user_id ON change_requests (user_id);
CREATE INDEX IF NOT EXISTS idx_change_requests_status ON change_requests (status);
CREATE INDEX IF NOT EXISTS idx_change_requests_timestamp ON change_requests (timestamp DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_profile_user_id ON user_profile (user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_pii_user_id ON user_pii (user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_employment_user_id ON user_employment (user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_banking_user_id ON user_banking (user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_family_user_id ON user_family (user_id);

CREATE INDEX IF NOT EXISTS idx_user_spouses_user_id ON user_spouses (user_id);
CREATE INDEX IF NOT EXISTS idx_user_dependents_user_id ON user_dependents (user_id);
CREATE INDEX IF NOT EXISTS idx_user_vehicles_user_id ON user_vehicles (user_id);
CREATE INDEX IF NOT EXISTS idx_user_documents_user_id ON user_documents (user_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_devices_device_code ON devices (device_code);
CREATE INDEX IF NOT EXISTS idx_tickets_device_id ON tickets (device_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status);
CREATE INDEX IF NOT EXISTS idx_tickets_last_updated ON tickets (last_updated DESC);
