# Clarus — Clearer IT, Faster Fixes 🛠️

**Clarus** is a streamlined IT support management platform built with Flask. It has grown from an IT support tool into a broader internal operations platform with ticketing, asset management, employee records, approvals, and self-service workflows.

---

## 🔧 Features

1. **Ticket Logging**: Submit detailed support tickets including user name, device ID, and issue description.
2. **Status Tracking**: Track each issue through statuses — *Open*, *In Progress*, and *Resolved*.
3. **Troubleshooting Logs**: Document troubleshooting steps and maintain a historical log for transparency and learning.
4. **Dynamic Dashboard**: Access a searchable, filterable, and sortable dashboard for all active tickets.
5. **Recent Activity Feed**: View the five most recently updated tickets for rapid context.
6. **Secure by Design**: Local-first storage with environment-based credentials, avoiding hardcoded secrets.

---

## 📋 Development Roadmap

### ✅ Phase 1: Foundation Build (v0.1)

- [x] Add, update, delete ticket functionality
- [x] Basic troubleshooting documentation per ticket
- [x] Status selection and update
- [x] Dashboard for all tickets
- [x] Recent updates feed
- [x] Search and filter by query or status

### 🧩 Phase 2: Enhancements (v0.2)

- [ ] Scaling troubleshooting details (more columns, more info can be manipulated)
- [ ] Role-based access (admin vs user)
- [ ] Device history log
- [ ] Sort and prioritize based on urgency
- [ ] File upload for screenshots or logs
- [ ] Email notification system (MFA alerts or ticket status updates)

### 🎯 Phase 3: Quality of Life

- [ ] Export tickets to PDF or CSV
- [ ] Mobile-responsive layout
- [ ] Custom themes per department
- [ ] Dark mode toggle

---

## 🧪 Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML + CSS (Vanilla + Templates)
- **Authentication**: Environment-based credentials
- **Deployment**: Local server; GitHub Repository

---

## 🛡️ Environment & Setup

1. Create a `.env` file in the root directory:
   ```bash
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=youruser
   POSTGRES_PASSWORD=yourpassword
   POSTGRES_DB=itflask
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
   flask run
   ```

## 🗃️ Database Notes

- The app now uses PostgreSQL through `psycopg2`, not MySQL.
- The repo-owned baseline schema lives at `database/migrations/001_postgres_baseline.sql`.
- The migration runner tracks applied files in a `schema_migrations` table inside your configured PostgreSQL schema.
- If your old local database was partially migrated from MySQL, run the migration script before testing any route changes.

---

## 🙌 About the Name

**Clarus** (Latin: *clear*, *bright*) is named in tribute to the my support systems (family, friends, and my partner) whose constant encouragement inspired the clarity, purpose, and structure behind this tool.

---

## 📌 Status

🟢 **Active Development**
