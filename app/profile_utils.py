from .db import get_db_connection

# ───── SETUP ─────
def create_empty_profile_if_missing(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT IGNORE INTO user_profile (user_id) VALUES (%s)", (user_id,))
    cursor.execute("INSERT IGNORE INTO user_pii (user_id) VALUES (%s)", (user_id,))
    cursor.execute("INSERT IGNORE INTO user_employment (user_id) VALUES (%s)", (user_id,))
    cursor.execute("INSERT IGNORE INTO user_banking (user_id) VALUES (%s)", (user_id,))
    cursor.execute("INSERT IGNORE INTO user_family (user_id) VALUES (%s)", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()

# ───── BASIC INFO ─────
def get_user_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def update_user_profile(user_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   UPDATE user_profile
                   SET full_name      = %s,
                       date_of_birth  = %s,
                       gender         = %s,
                       contact_number = %s,
                       address        = %s,
                       last_updated   = CURRENT_TIMESTAMP
                   WHERE user_id = %s
                   ''', (
                       data.get('full_name'), data.get('date_of_birth'), data.get('gender'),
                       data.get('contact_number'), data.get('address'), user_id
                   ))
    conn.commit()
    cursor.close()
    conn.close()

# ───── PII ─────
def get_user_pii(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_pii WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def update_user_pii(user_id, data_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_pii
        SET id_type = %s, id_number = %s, citizenship = %s,
            emergency_contact_name = %s, emergency_contact_number = %s,
            emergency_contact_address = %s
        WHERE user_id = %s
    """, (
        data_dict['id_type'], data_dict['id_number'], data_dict['citizenship'],
        data_dict['emergency_contact_name'], data_dict['emergency_contact_number'],
        data_dict['emergency_contact_address'], user_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

# ───── EMPLOYMENT ─────
def get_user_employment(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_employment WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def update_user_employment(user_id, data_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_employment
        SET job_title = %s, department = %s, work_email = %s,
            date_joined = %s, employment_status = %s, supervisor = %s
        WHERE user_id = %s
    """, (
        data_dict['job_title'], data_dict['department'], data_dict['work_email'],
        data_dict['date_joined'], data_dict['employment_status'], data_dict['supervisor'], user_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

# ───── BANKING ─────
def get_user_banking(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_banking WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def update_user_banking(user_id, data_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_banking
        SET bank_name = %s, bank_account_number = %s, account_holder_name = %s
        WHERE user_id = %s
    """, (
        data_dict['bank_name'], data_dict['bank_account_number'], data_dict['account_holder_name'], user_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

# ───── FAMILY ─────
def get_user_family(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_family WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def update_user_family(user_id, data_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_family
        SET marital_status = %s, spouse_name = %s, spouse_id_type = %s,
            spouse_id_number = %s, spouse_address = %s
        WHERE user_id = %s
    """, (
        data_dict['marital_status'], data_dict['spouse_name'], data_dict['spouse_id_type'],
        data_dict['spouse_id_number'], data_dict['spouse_address'], user_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_children(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_children WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def insert_user_child(user_id, name, dob):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_children (user_id, child_name, child_dob) VALUES (%s, %s, %s)",
                   (user_id, name, dob))
    conn.commit()
    cursor.close()
    conn.close()

def delete_user_child(child_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_children WHERE id = %s", (child_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ───── VEHICLES ─────
def get_user_vehicles(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_vehicles WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def add_user_vehicle(user_id, data_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_vehicles (user_id, vehicle_type, make_model, plate_number,
                                   color, parking_permit_id, parking_lot)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id, data_dict['vehicle_type'], data_dict['make_model'], data_dict['plate_number'],
        data_dict['color'], data_dict['parking_permit_id'], data_dict['parking_lot']
    ))
    conn.commit()
    cursor.close()
    conn.close()

# ───── DOCUMENTS ─────
def get_user_documents(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_documents WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def add_user_document(user_id, document_type, file_path, status="Pending"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_documents (user_id, document_type, file_path, status)
        VALUES (%s, %s, %s, %s)
    """, (user_id, document_type, file_path, status))
    conn.commit()
    cursor.close()
    conn.close()