# Clarus — Employee Records, Requests, and Self-Service

**Clarus** is an internal HR and employee self-service platform built with Flask. It is designed to centralize employee records, document handling, profile change requests, approvals, and role-based access in one internal portal.

---

## 🔧 Features

1. **Employee Profiles**: Manage employee personal, employment, banking, family, and identity information.
2. **Self-Service Updates**: Let employees submit profile changes instead of editing sensitive fields directly.
3. **Document Handling**: Upload and review employee documents in one place.
4. **Approval Workflow**: Review, approve, or decline change requests through an internal queue.
5. **Role-Based Access**: Separate employee, HR, support, and admin experiences.
6. **Secure by Design**: Local-first storage with environment-based credentials, avoiding hardcoded secrets.

---

## 📋 Development Roadmap

### ✅ V1: HR Self-Service Core

- [x] Authentication and session handling
- [x] Role-based access for admin, HR, support, and employee roles
- [x] Employee profile sections for personal, employment, family, banking, and identity data
- [x] Change request submission flow
- [x] HR/admin review queue for employee updates
- [x] Employee document uploads
- [x] Internal notifications

### 🧩 V1.5: Stabilization and UX

- [ ] Better portal/dashboard copy and consistency
- [ ] Stronger approval queue filtering and review workflow
- [ ] Search across employees and requests
- [ ] Better validation for uploads and change requests
- [ ] Test coverage for auth, profile, and approvals
- [ ] Clearer architecture and contributor documentation

### 🎯 V2: Operations Expansion

- [ ] Employee onboarding and offboarding workflows
- [ ] Department-friendly reporting and exports
- [ ] Employee-issued asset tracking refinement
- [ ] IT ticketing and troubleshooting as a secondary module
- [ ] Device history and support workflows

---

## 🧪 Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: Jinja templates, Bootstrap, HTMX, and light vanilla JavaScript
- **Authentication**: Environment-based credentials
- **Deployment**: Local server; GitHub repository

---

## 🛡️ Environment & Setup

1. Create a `.env` file in the root directory:
   ```bash
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=youruser
   POSTGRES_PASSWORD=yourpassword
   POSTGRES_DB=clarusdb
   POSTGRES_SCHEMA=public
   SECRET_KEY=yoursecretkey
   SALT=yoursalt
   ```

2. Make sure PostgreSQL exists and the target database is created.

3. Apply the baseline migration:
   ```bash
   python scripts/apply_postgres_migrations.py
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Development reload:
   - `run.py` uses Flask's built-in debug reloader.
   - Python and template changes restart the development server automatically.
   - You may still need a browser refresh to see updated page output.

## 🗃️ Database Notes

- The app uses PostgreSQL through `psycopg2`, not MySQL.
- The repo-owned baseline schema lives at `database/migrations/001_postgres_baseline.sql`.
- The migration runner tracks applied files in a `schema_migrations` table inside your configured PostgreSQL schema.
- If your old local database was partially migrated from MySQL, run the migration script before testing any route changes.

---

## 🙌 About the Name

**Clarus** (Latin: *clear*, *bright*) is named in tribute to the my support systems (family, friends, and my partner) whose constant encouragement inspired the clarity, purpose, and structure behind this tool.

---

## 📌 Status

🟢 **Active Development**

Current product direction:
- HR-first employee self-service portal
- IT support and troubleshooting retained as a later supporting module
