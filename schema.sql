CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    device_id VARCHAR(255),
    issue_description TEXT NOT NULL,
    date_reported DATE NOT NULL,
    troubleshooting TEXT,
    status VARCHAR(50) DEFAULT 'Open'
);

