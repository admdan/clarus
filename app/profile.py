from flask import Blueprint, render_template, request, abort, current_app
from flask_login import login_required, current_user
from .db import get_db_connection
from .profile_utils import (
    create_empty_profile_if_missing,
    update_user_profile, get_user_profile,
    update_user_pii, get_user_pii,
    update_user_employment, get_user_employment,
    update_user_banking, get_user_banking,
    update_user_vehicle, get_user_vehicles, get_vehicle_by_id, delete_user_vehicle, add_user_vehicle,
    update_user_family, get_user_family,
    get_user_spouses, add_user_spouse, update_user_spouse, delete_user_spouse,
    get_user_dependents, add_user_dependent, update_user_dependent, delete_user_dependent,
    get_user_documents, add_user_document,
    update_user_profile_picture, get_user_profile_picture, allowed_file
)
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os, uuid, mimetypes, subprocess

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

def get_target_user_id():
    # Returns the user ID being viewed or edited, ensuring role-based access control.
    user_id = request.args.get('user_id', type=int) or current_user.id
    if user_id != current_user.id and current_user.role not in ['admin', 'hr', 'support']:
        abort(403)
    return user_id

@profile_bp.route('/')
@login_required
def view_profile():
    user_id = get_target_user_id()
    create_empty_profile_if_missing(user_id)
    profile_data = get_full_profile(user_id)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT * FROM assets
        WHERE assigned_to = %s
        ORDER BY asset_id DESC
    ''', (user_id,))
    assigned_assets = cursor.fetchall()

    cursor.execute("SELECT email, role, username FROM users WHERE id = %s", (user_id,))
    user_account = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('profile.html', assigned_assets=assigned_assets, profile=profile_data, user_id=user_id, viewed_user_email=user_account['email'],
    viewed_user_role=user_account['role'])

def get_full_profile(user_id):
    conn = get_db_connection()
    profile = {}
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", (user_id,))
        profile['basic'] = cursor.fetchone()

        cursor.execute("SELECT * FROM user_pii WHERE user_id = %s", (user_id,))
        profile['pii'] = cursor.fetchone()

        cursor.execute("SELECT * FROM user_employment WHERE user_id = %s", (user_id,))
        profile['employment'] = cursor.fetchone()

        cursor.execute("SELECT * FROM user_banking WHERE user_id = %s", (user_id,))
        profile['bank'] = cursor.fetchone()

        cursor.execute("SELECT * FROM user_family WHERE user_id = %s", (user_id,))
        profile['family'] = cursor.fetchone()

        cursor.execute("SELECT * FROM user_spouses WHERE user_id = %s", (user_id,))
        profile['spouses'] = cursor.fetchall()

        cursor.execute("SELECT * FROM user_dependents WHERE user_id = %s", (user_id,))
        profile['dependents'] = cursor.fetchall()

        cursor.execute("SELECT * FROM user_vehicles WHERE user_id = %s", (user_id,))
        profile['vehicles'] = cursor.fetchall()

        cursor.execute("SELECT * FROM user_documents WHERE user_id = %s", (user_id,))
        profile['documents'] = cursor.fetchall()

        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        profile['username'] = cursor.fetchone()['username']

    conn.close()
    return profile

@profile_bp.route('/basic')
@login_required
def basic_info():
    user_id = get_target_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/basic_info.html', profile=profile, user_id=user_id)

@profile_bp.route('/edit_basic_info', methods=['GET'])
@login_required
def edit_basic_info():
    user_id = get_target_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", (user_id,))
    profile_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/edit_basic_info.html', profile=profile_data, user_id=user_id)

@profile_bp.route('/update_basic_info', methods=['POST'])
@login_required
def update_basic_info():
    user_id = get_target_user_id()
    form_data = {
        'full_name': request.form.get('full_name') or None,
        'date_of_birth': request.form.get('date_of_birth') or None,
        'gender': request.form.get('gender') or None,
        'contact_number': request.form.get('contact_number') or None,
        'address': request.form.get('address') or None,
    }
    update_user_profile(user_id, form_data)
    updated_profile = get_user_profile(user_id)
    return render_template('profile_sections/basic_info.html', profile=updated_profile, user_id=user_id)

@profile_bp.route('/pii')
@login_required
def pii_info():
    user_id = get_target_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_pii WHERE user_id = %s", (user_id,))
    pii = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/pii_info.html', pii=pii, user_id=user_id)

@profile_bp.route('/edit_pii_info', methods=['GET'])
@login_required
def edit_pii_info():
    user_id = get_target_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_pii WHERE user_id = %s", (user_id,))
    pii_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/edit_pii_info.html', pii=pii_data, user_id=user_id)

@profile_bp.route('/update_pii_info', methods=['POST'])
@login_required
def update_pii_info():
    user_id = get_target_user_id()
    form_data = {
        'id_type': request.form.get('id_type') or None,
        'id_number': request.form.get('id_number') or None,
        'citizenship': request.form.get('citizenship') or None,
        'emergency_contact_name': request.form.get('emergency_contact_name') or None,
        'emergency_contact_number': request.form.get('emergency_contact_number') or None,
        'emergency_contact_address': request.form.get('emergency_contact_address') or None,
    }
    update_user_pii(user_id, form_data)
    updated_pii = get_user_pii(user_id)
    return render_template('profile_sections/pii_info.html', pii=updated_pii, user_id=user_id)

@profile_bp.route('/employment')
@login_required
def employment_info():
    user_id = get_target_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_employment WHERE user_id = %s", (user_id,))
    employment = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/employment_info.html', employment=employment, user_id=user_id)

@profile_bp.route('/edit_employment_info', methods=['GET'])
@login_required
def edit_employment_info():
    user_id = get_target_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_employment WHERE user_id = %s", (user_id,))
    employment_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/edit_employment_info.html', employment=employment_data, user_id=user_id)

@profile_bp.route('/update_employment_info', methods=['POST'])
@login_required
def update_employment_info():
    user_id = get_target_user_id()
    form_data = {
        'job_title': request.form.get('job_title') or None,
        'department': request.form.get('department') or None,
        'work_email': request.form.get('work_email') or None,
        'date_joined': request.form.get('date_joined') or None,
        'employment_status': request.form.get('employment_status') or None,
        'supervisor': request.form.get('supervisor') or None,
    }
    update_user_employment(user_id, form_data)
    updated_employment = get_user_employment(user_id)
    return render_template('profile_sections/employment_info.html', employment=updated_employment, user_id=user_id)

@profile_bp.route('/banking')
@login_required
def banking_info():
    user_id = get_target_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_banking WHERE user_id = %s", (user_id,))
    banking = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/banking_info.html', banking=banking, user_id=user_id)

@profile_bp.route('/edit_banking_info', methods=['GET'])
@login_required
def edit_banking_info():
    user_id = get_target_user_id()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_banking WHERE user_id = %s", (user_id,))
    banking_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/edit_banking_info.html', banking=banking_data, user_id=user_id)

@profile_bp.route('/update_banking_info', methods=['POST'])
@login_required
def update_banking_info():
    user_id = get_target_user_id()
    form_data = {
        'bank_name': request.form.get('bank_name') or None,
        'bank_account_number': request.form.get('bank_account_number') or None,
        'account_holder_name': request.form.get('account_holder_name') or None,
    }
    update_user_banking(user_id, form_data)
    updated_banking = get_user_banking(user_id)
    return render_template('profile_sections/banking_info.html', banking=updated_banking, user_id=user_id)

@profile_bp.route('/vehicles')
@login_required
def vehicles_info():
    user_id = get_target_user_id()
    vehicles = get_user_vehicles(user_id)
    return render_template('profile_sections/vehicles_info.html', vehicles=vehicles, user_id=user_id)

@profile_bp.route('/add_vehicle_info', methods=['GET', 'POST'])
@login_required
def add_vehicles_info():
    user_id = get_target_user_id()
    if request.method == 'POST':
        form_data = {
            'vehicle_type': request.form.get('vehicle_type') or None,
            'make': request.form.get('make') or None,
            'model': request.form.get('model') or None,
            'year_model': request.form.get('year_model') or None,
            'plate_number': request.form.get('plate_number') or None,
            'color': request.form.get('color') or None,
            'parking_permit_id': request.form.get('parking_permit_id') or None
        }
        add_user_vehicle(user_id, form_data)
        vehicles = get_user_vehicles(user_id)
        return render_template('profile_sections/vehicles_info.html', vehicles=vehicles, user_id=user_id)
    return render_template('profile_sections/edit_vehicles_info.html', vehicle=None, user_id=user_id)

@profile_bp.route('/edit_vehicles_info/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicles_info(vehicle_id):
    user_id = get_target_user_id()
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or (vehicle['user_id'] != user_id and current_user.role not in ['admin', 'hr', 'support']):
        abort(403)

    if request.method == 'POST':
        form_data = {
            'vehicle_type': request.form.get('vehicle_type') or None,
            'make': request.form.get('make') or None,
            'model': request.form.get('model') or None,
            'year_model': request.form.get('year_model') or None,
            'plate_number': request.form.get('plate_number') or None,
            'color': request.form.get('color') or None,
            'parking_permit_id': request.form.get('parking_permit_id') or None
        }
        update_user_vehicle(vehicle_id, form_data)
        vehicles = get_user_vehicles(user_id)
        return render_template('profile_sections/vehicles_info.html', vehicles=vehicles, user_id=user_id)

    return render_template('profile_sections/edit_vehicles_info.html', vehicle=vehicle, user_id=user_id)

@profile_bp.route('/delete_vehicle_info/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicles_info(vehicle_id):
    user_id = get_target_user_id()
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or (vehicle['user_id'] != user_id and current_user.role not in ['admin', 'hr', 'support']):
        abort(403)

    delete_user_vehicle(vehicle_id)
    vehicles = get_user_vehicles(user_id)
    return render_template('profile_sections/vehicles_info.html', vehicles=vehicles, user_id=user_id)

@profile_bp.route('/family')
@login_required
def family_info():
    user_id = get_target_user_id()
    family = get_user_family(user_id)
    spouses = get_user_spouses(user_id)
    dependents = get_user_dependents(user_id)
    return render_template(
        'profile_sections/family_info.html',
        family=family,
        spouses=spouses,
        dependents=dependents,
        user_id=user_id
    )

@profile_bp.route('/edit_family_info', methods=['GET'])
@login_required
def edit_family_info():
    user_id = get_target_user_id()
    family_data = get_user_family(user_id)
    return render_template('profile_sections/edit_family_info.html', family=family_data, user_id=user_id)

@profile_bp.route('/update_family_info', methods=['POST'])
@login_required
def update_family_info():
    user_id = get_target_user_id()
    form_data = {
        'marital_status': request.form.get('marital_status') or None,
    }
    update_user_family(user_id, form_data)
    family_data = {
        'family': get_user_family(user_id),
        'spouses': get_user_spouses(user_id),
        'dependents': get_user_dependents(user_id),
        'user_id': user_id
    }
    return render_template('profile_sections/family_info.html', **family_data)

@profile_bp.route('/add_spouse_info', methods=['GET', 'POST'])
@login_required
def add_spouse_info():
    user_id = get_target_user_id()
    if request.method == 'POST':
        form_data = {
            'spouse_name': request.form.get('spouse_name'),
            'spouse_id_type': request.form.get('spouse_id_type'),
            'spouse_id_number': request.form.get('spouse_id_number'),
            'spouse_address': request.form.get('spouse_address')
        }
        add_user_spouse(user_id, form_data)
        family_data = {
            'family': get_user_family(user_id),
            'spouses': get_user_spouses(user_id),
            'dependents': get_user_dependents(user_id),
            'user_id': user_id
        }
        return render_template('profile_sections/family_info.html', **family_data)
    return render_template('profile_sections/edit_spouse_info.html', spouse=None, user_id=user_id)

@profile_bp.route('/edit_spouse_info/<int:spouse_id>', methods=['GET', 'POST'])
@login_required
def edit_spouse_info(spouse_id):
    user_id = get_target_user_id()
    if request.method == 'POST':
        form_data = {
            'spouse_name': request.form.get('spouse_name'),
            'spouse_id_type': request.form.get('spouse_id_type'),
            'spouse_id_number': request.form.get('spouse_id_number'),
            'spouse_address': request.form.get('spouse_address')
        }
        update_user_spouse(spouse_id, form_data)
        family_data = {
            'family': get_user_family(user_id),
            'spouses': get_user_spouses(user_id),
            'dependents': get_user_dependents(user_id),
            'user_id': user_id
        }
        return render_template('profile_sections/family_info.html', **family_data)

    spouses = get_user_spouses(user_id)
    spouse = next((s for s in spouses if s['id'] == spouse_id), None)
    return render_template('profile_sections/edit_spouse_info.html', spouse=spouse, user_id=user_id)

@profile_bp.route('/delete_spouse_info/<int:spouse_id>', methods=['POST'])
@login_required
def delete_spouse_info(spouse_id):
    user_id = get_target_user_id()
    delete_user_spouse(spouse_id)
    family_data = {
        'family': get_user_family(user_id),
        'spouses': get_user_spouses(user_id),
        'dependents': get_user_dependents(user_id),
        'user_id': user_id
    }
    return render_template('profile_sections/family_info.html', **family_data)

@profile_bp.route('/add_dependent_info', methods=['GET', 'POST'])
@login_required
def add_dependent_info():
    user_id = get_target_user_id()
    if request.method == 'POST':
        form_data = {
            'dependent_name': request.form.get('dependent_name'),
            'dependent_relationship': request.form.get('dependent_relationship'),
            'dependent_birthdate': request.form.get('dependent_birthdate'),
            'dependent_notes': request.form.get('dependent_notes')
        }
        add_user_dependent(user_id, form_data)
        family_data = {
            'family': get_user_family(user_id),
            'spouses': get_user_spouses(user_id),
            'dependents': get_user_dependents(user_id),
            'user_id': user_id
        }
        return render_template('profile_sections/family_info.html', **family_data)
    return render_template('profile_sections/edit_dependent_info.html', dependent=None, user_id=user_id)

@profile_bp.route('/edit_dependent_info/<int:dependent_id>', methods=['GET', 'POST'])
@login_required
def edit_dependent_info(dependent_id):
    user_id = get_target_user_id()
    if request.method == 'POST':
        form_data = {
            'dependent_name': request.form.get('dependent_name'),
            'dependent_relationship': request.form.get('dependent_relationship'),
            'dependent_birthdate': request.form.get('dependent_birthdate'),
            'dependent_notes': request.form.get('dependent_notes')
        }
        update_user_dependent(dependent_id, form_data)
        family_data = {
            'family': get_user_family(user_id),
            'spouses': get_user_spouses(user_id),
            'dependents': get_user_dependents(user_id),
            'user_id': user_id
        }
        return render_template('profile_sections/family_info.html', **family_data)

    dependents = get_user_dependents(user_id)
    dependent = next((d for d in dependents if d['id'] == dependent_id), None)
    return render_template('profile_sections/edit_dependent_info.html', dependent=dependent, user_id=user_id)

@profile_bp.route('/delete_dependent_info/<int:dependent_id>', methods=['POST'])
@login_required
def delete_dependent_info(dependent_id):
    user_id = get_target_user_id()
    delete_user_dependent(dependent_id)
    family_data = {
        'family': get_user_family(user_id),
        'spouses': get_user_spouses(user_id),
        'dependents': get_user_dependents(user_id),
        'user_id': user_id
    }
    return render_template('profile_sections/family_info.html', **family_data)

def is_file_safe(filepath):
    try:
        abs_path = os.path.abspath(filepath)
        result = subprocess.run(['clamscan', abs_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        return b"Infected files: 0" in result.stdout
    except Exception as e:
        print("Error:", e)
        return False

@profile_bp.route('/documents')
@login_required
def document_info():
    user_id = get_target_user_id()
    documents = get_user_documents(user_id)
    return render_template('profile_sections/document_info.html', documents=documents, user_id=user_id)

@profile_bp.route('/upload_documents', methods=['POST'])
@login_required
def upload_documents():
    user_id = get_target_user_id()
    if user_id != current_user.id and current_user.role not in ['admin', 'hr', 'support']:
        abort(403)

    file = request.files.get('document')
    doc_type = request.form.get('document_type')
    display_name = request.form.get('display_name')

    if not file or not file.filename or '.' not in file.filename:
        return "Invalid file", 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return "Invalid file type", 400

    safe_doc_type = doc_type.replace(" ", "_")
    unique_filename = f"user{user_id}-{safe_doc_type}-{uuid.uuid4().hex[:8]}.{ext}"
    user_folder = os.path.join(UPLOAD_FOLDER, f"user_{user_id}")
    os.makedirs(user_folder, exist_ok=True)

    file_path = f"user_{user_id}/{unique_filename}"
    save_path = os.path.join(user_folder, unique_filename)

    file_contents = file.read()

    guessed_type, _ = mimetypes.guess_type(file.filename)
    if guessed_type not in ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']:
        return "Invalid MIME type.", 400

    with open(save_path, 'wb') as f:
        f.write(file_contents)

    if not is_file_safe(save_path):
        os.remove(save_path)
        return "Upload blocked: virus detected.", 400

    add_user_document(user_id, doc_type, file_path, display_name=display_name)
    documents = get_user_documents(user_id)
    return render_template('profile_sections/document_info.html', documents=documents, user_id=user_id)

@profile_bp.route('/delete_document/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    user_id = get_target_user_id()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_documents WHERE id = %s AND user_id = %s", (doc_id, user_id))
    doc = cursor.fetchone()

    if not doc:
        cursor.close()
        conn.close()
        return "Not found", 404

    try:
        file_full_path = os.path.join(UPLOAD_FOLDER, doc['file_path'])
        if os.path.exists(file_full_path):
            os.remove(file_full_path)
    except FileNotFoundError:
        pass

    cursor.execute("DELETE FROM user_documents WHERE id = %s", (doc_id,))
    conn.commit()
    cursor.close()
    conn.close()

    documents = get_user_documents(user_id)
    return render_template('profile_sections/document_info.html', documents=documents, user_id=user_id)

@profile_bp.route('/profile_picture')
@login_required
def profile_picture_info():
    user_id = get_target_user_id()
    folder_path = os.path.join(current_app.root_path, 'static', 'uploads', f"user_{user_id}", "profile_pictures")
    profile_picture_filename = None

    if os.path.exists(folder_path):
        files = sorted(os.listdir(folder_path), key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
        if files:
            profile_picture_filename = f"user_{user_id}/profile_pictures/{files[0]}"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    timestamp = int(datetime.now(timezone.utc).timestamp())
    return render_template('profile_sections/profile_picture.html',
                           profile_picture_filename=profile_picture_filename,
                           timestamp=timestamp,
                           user_id=user_id,
                           username=row['username'] if row else 'User')

@profile_bp.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    user_id = get_target_user_id()
    if user_id != current_user.id and current_user.role not in ['admin', 'hr', 'support']:
        abort(403)

    file = request.files.get('profile_picture')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        folder_path = os.path.join(current_app.root_path, 'static', 'uploads', f"user_{user_id}", "profile_pictures")
        os.makedirs(folder_path, exist_ok=True)

        for f in os.listdir(folder_path):
            try:
                os.remove(os.path.join(folder_path, f))
            except:
                continue

        file_path = os.path.join(folder_path, unique_filename)
        file.save(file_path)

        timestamp = int(datetime.now(timezone.utc).timestamp())
        return render_template('profile_sections/profile_picture.html',
                               profile_picture_filename=unique_filename,
                               timestamp=timestamp,
                               user_id=user_id)

    error = "Invalid file or file type."
    return render_template('profile_sections/profile_picture.html', error=error, user_id=user_id)

@profile_bp.route('/request_change', methods=['POST'])
@login_required
def request_change():
    user_id = get_target_user_id()
    if user_id != current_user.id:
        abort(403)

    data = request.get_json()
    field = data.get('field')
    new_value = data.get('new_value', '')
    note = data.get('note', '')

    if not field:
        return {"error": "Missing field"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO change_requests (user_id, field_requested, new_value, note, timestamp)
        VALUES (%s, %s, %s, %s, NOW())
    ''', (user_id, field, new_value, note))
    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "ok"}, 200