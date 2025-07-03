# asset.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, make_response
from flask_login import login_required, current_user
from .db import get_db_connection
from .routes import roles_required
from datetime import datetime
from io import StringIO
from weasyprint import HTML, CSS
import csv, json

asset_bp = Blueprint('asset', __name__, url_prefix='/assets')

@asset_bp.route('/')
@login_required
@roles_required('admin', 'hr', 'support')
def inventory_dashboard():

    # Filters & search
    device_type = request.args.get('device_type')
    status = request.args.get('status')
    search = request.args.get('search')

    # Pagination
    page = request.args.get('page', default=1, type=int)
    per_page = 10  # Trying with 10 first, can also go to 20/25
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = '''
            SELECT a.*, u.username AS assigned_user
            FROM assets a
                     LEFT JOIN users u ON a.assigned_to = u.id
            WHERE 1 = 1
            '''
    count_query = '''
                  SELECT COUNT(*) as total
                  FROM assets a
                           LEFT JOIN users u ON a.assigned_to = u.id
                  WHERE 1=1
                  '''
    values = []

    if device_type:
        query += ' AND a.device_type = %s'
        count_query += ' AND a.device_type = %s'
        values.append(device_type)
    if status:
        query += ' AND a.status = %s'
        count_query += ' AND a.status = %s'
        values.append(status)
    if search:
        query += ' AND (a.serial_number LIKE %s OR u.username LIKE %s)'
        count_query += ' AND (a.serial_number LIKE %s OR u.username LIKE %s)'
        values.extend([f"%{search}%", f"%{search}%"])

    # Limit & offset
    query += ' ORDER BY a.asset_id DESC LIMIT %s OFFSET %s;'
    values.extend([per_page, offset])

    cursor.execute(query, tuple(values))
    assets = cursor.fetchall()

    # Get total count for pagination
    cursor.execute(count_query, tuple(values[:-2])) # Exclude limit/offset
    total = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    total_pages = (total + per_page - 1 ) // per_page

    base_query = request.args.to_dict()
    base_query.pop('page', None)  # Remove existing page param if present

    # Build pagination URLs in Python
    pagination_urls = {
        'prev': url_for('asset.inventory_dashboard', **base_query, page=page - 1) if page > 1 else None,
        'next': url_for('asset.inventory_dashboard', **base_query, page=page + 1) if page < total_pages else None,
        'pages': [url_for('asset.inventory_dashboard', **base_query, page=p) for p in range(1, total_pages + 1)]
    }

    return render_template('aims.html', assets=assets, page=page, total_pages=total_pages, total=total, base_query=base_query, pagination_urls=pagination_urls)

@asset_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'hr', 'support')
def add_asset():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        device_type = request.form['device_type']
        serial_number = request.form['serial_number']
        condition = request.form['condition']
        status = request.form['status']
        date_assigned = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #This is also auto-added
        added_by = current_user.id #  This is auto-added
        model = request.form['model']
        purchase_date = request.form['purchase_date']
        manufacturer = request.form['manufacturer'] or None
        remarks = request.form['remarks'] or None
        assigned_to = request.form.get('assigned_to') or None
        warranty_end = request.form['warranty_end'] or None
        location = request.form['location'] or None
        ip_mac = request.form['ip_mac'] or None
        asset_tag = request.form['asset_tag'] or None
        invoice_ref = request.form['invoice_ref'] or None

        # Required fields with flash warning
        if not all([device_type, serial_number, condition, status, model, purchase_date]):
            flash("Please fill in all required fields.", "danger")
            return redirect(request.url)

        cursor.execute('''
                       INSERT INTO assets 
                       (device_type, serial_number, `condition`, status, assigned_to, date_assigned, remarks, added_by,
                        model, manufacturer, purchase_date, warranty_end, location, ip_mac, asset_tag, invoice_ref)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                               %s, %s, %s, %s, %s, %s, %s, %s)
                       ''',
                       (device_type, serial_number, condition, status, assigned_to, date_assigned, remarks, added_by,
                        model, manufacturer, purchase_date, warranty_end, location, ip_mac, asset_tag, invoice_ref))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Asset added successfully!", "success")
        return redirect(url_for('asset.inventory_dashboard'))

    cursor.execute('''SELECT id, username FROM users''')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('asset_form.html', users=users, mode='add')

@asset_bp.route('/edit/<int:asset_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'hr', 'support')
def edit_asset(asset_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        device_type = request.form['device_type']
        serial_number = request.form['serial_number']
        condition = request.form['condition']
        status = request.form['status']
        model = request.form['model']
        purchase_date = request.form['purchase_date']
        manufacturer = request.form['manufacturer'] or None
        remarks = request.form['remarks'] or None
        assigned_to = request.form.get('assigned_to') or None
        warranty_end = request.form['warranty_end'] or None
        location = request.form['location'] or None
        ip_mac = request.form['ip_mac'] or None
        asset_tag = request.form['asset_tag'] or None
        invoice_ref = request.form['invoice_ref'] or None

        # Required fields with flash warning
        if not all([device_type, serial_number, condition, status, model, purchase_date]):
            flash("Please fill in all required fields.", "danger")
            return redirect(request.url)

        cursor.execute('''
            UPDATE assets
            SET device_type = %s,
                serial_number = %s,
                `condition` = %s,
                status = %s,
                assigned_to = %s,
                remarks = %s,
                model = %s,
                manufacturer = %s,
                purchase_date = %s,
                warranty_end = %s,
                location = %s,
                ip_mac = %s,
                asset_tag = %s,
                invoice_ref = %s,
                last_updated = CURRENT_TIMESTAMP
            WHERE asset_id = %s
        ''', (device_type, serial_number, condition, status, assigned_to, remarks, model, manufacturer,
              purchase_date, warranty_end, location, ip_mac, asset_tag, invoice_ref, asset_id))

        conn.commit()
        cursor.close()
        conn.close()
        flash("Asset updated successfully!", "success")
        return redirect(url_for('asset.inventory_dashboard'))

    # GET method to fetch current asset and user list
    cursor.execute("SELECT * FROM assets WHERE asset_id = %s", (asset_id,))
    asset = cursor.fetchone()

    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    if not asset:
        flash("Asset not found.", "danger")
        return redirect(url_for('asset.inventory_dashboard'))

    return render_template('asset_form.html', asset=asset, users=users, mode='edit')

@asset_bp.route('/delete/<int:asset_id>', methods=['POST'])
@login_required
@roles_required('admin', 'hr', 'support')
def delete_asset(asset_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assets WHERE asset_id = %s", (asset_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Asset deleted successfully!", "success")
    return redirect(url_for('asset.inventory_dashboard'))

@asset_bp.route('/export_csv')
@login_required
@roles_required('admin', 'hr', 'support')
def export_csv():
    device_type = request.args.get('device_type')
    status = request.args.get('status')
    search = request.args.get('search')
    filename = request.args.get('filename', 'asset_inventory.csv')  # Fallback if none provided

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = '''
            SELECT a.*, u.username AS assigned_user
            FROM assets a
                     LEFT JOIN users u ON a.assigned_to = u.id
            WHERE 1 = 1
            '''
    values = []

    if device_type:
        query += ' AND a.device_type = %s'
        values.append(device_type)
    if status:
        query += ' AND a.status = %s'
        values.append(status)
    if search:
        query += ' AND (a.serial_number LIKE %s OR u.username LIKE %s)'
        values.extend([f"%{search}%", f"%{search}%"])

    cursor.execute(query, tuple(values))
    assets = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    headers = [
        'Asset ID', 'Device Type', 'Serial Number', 'Condition', 'Status',
        'Assigned To', 'Date Assigned', 'Remarks', 'Model', 'Manufacturer',
        'Purchase Date', 'Warranty End', 'Location', 'IP/MAC', 'Asset Tag',
        'Invoice Ref', 'Added By', 'Last Updated'
    ]
    writer.writerow(headers)

    for asset in assets:
        writer.writerow([
            asset['asset_id'], asset['device_type'], asset['serial_number'], asset['condition'],
            asset['status'], asset.get('assigned_user') or 'Unassigned', asset['date_assigned'],
            asset.get('remarks') or '', asset['model'], asset.get('manufacturer') or '',
            asset.get('purchase_date'), asset.get('warranty_end') or '', asset.get('location') or '',
            asset.get('ip_mac') or '', asset.get('asset_tag') or '', asset.get('invoice_ref') or '',
            asset['added_by'], asset['last_updated']
        ])

    output = si.getvalue()
    si.close()

    asset_ids = [a['asset_id'] for a in assets]
    filters = {'device_type': device_type, 'status': status, 'search': search}
    log_export_event(filename, "CSV", is_single_asset=False, filters_applied=filters, asset_ids=asset_ids)

    return Response(
        output,
        mimetype="text/csv",
        headers = {"Content-Disposition": f"attachment;filename={filename}"}
    )

@asset_bp.route('/pdf/<int:asset_id>')
@login_required
@roles_required('admin', 'hr', 'support')
def export_pdf(asset_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT a.*, u.username AS assigned_user
        FROM assets a
        LEFT JOIN users u ON a.assigned_to = u.id
        WHERE a.asset_id = %s
    ''', (asset_id,))
    asset = cursor.fetchone()
    cursor.close()
    conn.close()

    if not asset:
        flash("Asset not found.", "danger")
        return redirect(url_for('asset.inventory_dashboard'))

    html = render_template('asset_pdf.html', asset=asset)
    pdf = HTML(string=html).write_pdf()

    filename = f"{asset['device_type']}_{asset['serial_number']}.pdf"
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'

    log_export_event(filename, "PDF", is_single_asset=True, asset_ids=[asset_id])

    return response

@asset_bp.route('/export_pdf')
@login_required
@roles_required('admin', 'hr', 'support')
def export_pdf_all():
    device_type = request.args.get('device_type')
    status = request.args.get('status')
    search = request.args.get('search')
    filename = request.args.get('filename', 'asset_inventory.pdf')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = '''
        SELECT a.*, u.username AS assigned_user
        FROM assets a
        LEFT JOIN users u ON a.assigned_to = u.id
        WHERE 1 = 1
    '''
    values = []

    if device_type:
        query += ' AND a.device_type = %s'
        values.append(device_type)
    if status:
        query += ' AND a.status = %s'
        values.append(status)
    if search:
        query += ' AND (a.serial_number LIKE %s OR u.username LIKE %s)'
        values.extend([f"%{search}%", f"%{search}%"])

    cursor.execute(query, tuple(values))
    assets = cursor.fetchall()
    cursor.close()
    conn.close()

    html = render_template('asset_list.html', assets=assets)
    pdf = HTML(string=html).write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1cm; }')])

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'

    asset_ids = [a['asset_id'] for a in assets]
    filters = {'device_type': device_type, 'status': status, 'search': search}
    log_export_event(filename, "PDF", is_single_asset=False, filters_applied=filters, asset_ids=asset_ids)

    return response

def log_export_event(filename, export_type, is_single_asset=False, filters_applied=None, asset_ids=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    filters_json = json.dumps(filters_applied or {})
    asset_id_str = json.dumps(asset_ids) if asset_ids else None
    asset_count = len(asset_ids) if asset_ids else 0

    cursor.execute('''
        INSERT INTO export_logs (filename, user_id, export_type, is_single_asset, filters_applied,
                                 exported_asset_ids, num_assets, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    ''', (filename, current_user.id, export_type, is_single_asset, filters_json,
          asset_id_str, asset_count))
    conn.commit()
    cursor.close()
    conn.close()

@asset_bp.route('/export_logs')
@login_required
@roles_required('admin')
def view_export_logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT el.*, u.username
        FROM export_logs el
        JOIN users u ON el.user_id = u.id
        ORDER BY el.timestamp DESC
    ''')
    logs = cursor.fetchall()
    cursor.close()
    conn.close()

    for log in logs:
        try:
            log['filters'] = json.loads(log['filters_applied']) if log['filters_applied'] else {}
        except json.JSONDecodeError:
            log['filters'] = {}

        try:
            log['asset_ids'] = json.loads(log['exported_asset_ids']) if log['exported_asset_ids'] else []
        except json.JSONDecodeError:
            log['asset_ids'] = []

    return render_template('export_logs.html', logs=logs)


