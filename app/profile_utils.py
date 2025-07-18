from fileinput import filename
from datetime import datetime
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

    # Retrieve current values to preserve locked fields
    cursor.execute("SELECT full_name, date_of_birth, gender FROM user_profile WHERE user_id = %s", (user_id,))
    current = cursor.fetchone()

    # Preserve locked fields
    full_name = current[0]
    date_of_birth = current[1]
    gender = current[2]

    contact_number = data.get('contact_number')
    address = data.get('address')

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
        full_name, date_of_birth, gender, contact_number, address, user_id
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
        SET marital_status = %s
        WHERE user_id = %s
    """, (data_dict['marital_status'], user_id))
    conn.commit()
    cursor.close()
    conn.close()

# ───── SPOUSES ─────
def get_user_spouses(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_spouses WHERE user_id = %s", (user_id,))
    spouses = cursor.fetchall()
    cursor.close()
    conn.close()
    return spouses

def add_user_spouse(user_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_spouses (user_id, spouse_name, spouse_id_type, spouse_id_number, spouse_address)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user_id, data['spouse_name'], data['spouse_id_type'],
        data['spouse_id_number'], data['spouse_address']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def update_user_spouse(spouse_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_spouses
        SET spouse_name = %s, spouse_id_type = %s, spouse_id_number = %s, spouse_address = %s
        WHERE id = %s
    """, (
        data['spouse_name'], data['spouse_id_type'],
        data['spouse_id_number'], data['spouse_address'], spouse_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

def delete_user_spouse(spouse_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_spouses WHERE id = %s", (spouse_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ───── DEPENDENT ─────
def get_user_dependents(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_dependents WHERE user_id = %s", (user_id,))
    dependents = cursor.fetchall()
    cursor.close()
    conn.close()
    return dependents

def add_user_dependent(user_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_dependents (user_id, dependent_name, dependent_relationship, dependent_birthdate, dependent_notes)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user_id, data['dependent_name'], data['dependent_relationship'], data['dependent_birthdate'], data['dependent_notes']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def update_user_dependent(dependent_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_dependents
        SET dependent_name = %s, dependent_relationship = %s, dependent_birthdate = %s, dependent_notes = %s
        WHERE id = %s
    """, (
        data['dependent_name'], data['dependent_relationship'], data['dependent_birthdate'], data['dependent_notes']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def delete_user_dependent(dependent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_dependents WHERE id = %s", (dependent_id,))
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

def get_vehicle_by_id(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_vehicles WHERE id = %s", (vehicle_id,))
    vehicle = cursor.fetchone()
    cursor.close()
    conn.close()
    return vehicle

def add_user_vehicle(user_id, data_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_vehicles (user_id, vehicle_type, make, model, year_model, plate_number,
             color, parking_permit_id, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    ''', (
        user_id, data_dict['vehicle_type'], data_dict['make'], data_dict['model'], data_dict['year_model'], data_dict['plate_number'],
        data_dict['color'], data_dict['parking_permit_id']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def update_user_vehicle(vehicle_id, data_dict):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE user_vehicles
        SET vehicle_type = %s,
            make = %s,
            model = %s,
            year_model = %s,
            plate_number = %s,
            color = %s,
            parking_permit_id = %s,
            last_updated = CURRENT_TIMESTAMP
        WHERE id = %s
    ''', (
        data_dict['vehicle_type'],
        data_dict['make'],
        data_dict['model'],
        data_dict['year_model'],
        data_dict['plate_number'],
        data_dict['color'],
        data_dict['parking_permit_id'],
        vehicle_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

def delete_user_vehicle(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_vehicles WHERE id = %s", (vehicle_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ───── DOCUMENTS ─────
def get_user_documents(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
                   SELECT d.*, u.username
                   FROM user_documents d
                            JOIN users u ON d.user_id = u.id
                   WHERE d.user_id = %s
                   ORDER BY d.id DESC
                   ''', (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def add_user_document(user_id, document_type, file_path, status="Pending", display_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_documents (user_id, document_type, file_path, status, display_name)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, document_type, file_path, status, display_name))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_profile_picture(user_id):
    conn = get_db_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT profile_picture FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result["profile_picture"] if result else None

def update_user_profile_picture(user_id, file_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET profile_picture = %s WHERE id = %s", (file_path, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def update_field_and_timestamp(table, column, value, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"""
            UPDATE {table}
            SET {column} = %s,
                last_updated = %s
            WHERE user_id = %s
        """
        cursor.execute(query, (value, datetime.now(), user_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
