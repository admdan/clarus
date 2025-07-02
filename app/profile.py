from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .db import get_db_connection

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def view_profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT * FROM assets
        WHERE assigned_to = %s
        ORDER BY asset_id DESC
    ''', (current_user.id,))
    assigned_assets = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('profile.html', assigned_assets=assigned_assets)
