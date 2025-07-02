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

# Asset detail view (restricted to current user) #currently not using this because I opted for the inline view collapsible view button
#@profile_bp.route('/view/<int:asset_id>')
#@login_required
#def view_asset_detail(asset_id):
#    conn = get_db_connection()
#    cursor = conn.cursor(dictionary=True)
#
#    cursor.execute('''
#        SELECT * FROM assets
#        WHERE asset_id = %s AND assigned_to = %s
#    ''', (asset_id, current_user.id))
#    asset = cursor.fetchone()
#
#    cursor.close()
#    conn.close()
#
#    if not asset:
#        abort(404)  # Not found or not owned by current user
#
#    return render_template('view_asset_user.html', asset=asset)