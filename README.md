# Clarus — Clearer IT, Faster Fixes 🛠️

**Clarus** is a streamlined IT support management platform built with Flask. It offers a centralized system for tracking, updating, and resolving IT support tickets with enhanced troubleshooting workflows and user-friendly features.

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
- **Database**: MySQL
- **Frontend**: HTML + CSS (Vanilla + Templates)
- **Authentication**: Environment-based credentials
- **Deployment**: Local server; GitHub Repository

---

## 🛡️ Environment & Setup

1. Create a `.env` file in the root directory:
   ```bash
   MYSQL_HOST=localhost
   MYSQL_USER=youruser
   MYSQL_PASSWORD=yourpassword
   MYSQL_DB=itflask
   SECRET_KEY=yoursecretkey
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   flask run
   ```

---

## 🙌 About the Name

**Clarus** (Latin: *clear*, *bright*) is named in tribute to the my support systems (family, friends, and my partner) whose constant encouragement inspired the clarity, purpose, and structure behind this tool.

---

## 📌 Status

🟢 **Active Development**
