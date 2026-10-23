# Odoo for Hotel & Resort Management (PMS)

An enterprise-ready **Hotel & Resort Property Management System (PMS)** built on Odoo, featuring integrated **Front Desk Operations**, **Room & Reservation Management**, **Housekeeping**, **Police & Government Compliance (FRRO/Form C & FIR Tracker)**, and a **Payroll Management System**.

---

## 🌟 Modules Included

### 1. `mouli_hotels` - Comprehensive Hotel PMS
* **Property & Floor Management**: Multi-property, building, floor, and room category mapping.
* **Room Inventory & Real-Time Status**: Visual tracking of vacant, occupied, dirty, inspection, and out-of-order rooms.
* **Reservation Engine**: Real-time booking with automated double-booking prevention.
* **Front Desk Workflows**: Seamless guest check-in, check-out, room moves, and guest history.
* **Folios & Billing**: Consolidated guest stay billing, split folios, and direct invoice generation.
* **Housekeeping & Turnaround**: Auto-scheduled cleaning tasks, housekeeping room release workflows.
* **POS & Operations Integration**: Restaurant POS room-charging and maintenance request tickets.

### 2. `resort_compliance` - Police & Government Regulatory Compliance
* **Daily Police Intimations**: Automated guest and visitor intimation records for local law enforcement.
* **Foreign Guest / FRRO Form C Tracker**: Bureau of Immigration (BoI) compliant passport, visa, and entry logging.
* **Incident & FIR Register**: Document hotel incidents (theft, disputes, property damage, accidents) with police FIR references.
* **Police Visit Logs**: Official records of law enforcement inspections, inquiries, and station officer visits.
* **Security & Gate Logs**: Visitor pass management, vehicle entry/exit logs, CCTV & night patrol logs.
* **Access Control**: Confidential data restricted strictly to compliance and security officers.
* **Official PDF Reports**: One-click printable QWeb PDF reports formatted for police station submission.

### 3. `custom_payroll` - Easy Employee Payroll
* **Contracts & Wages**: Employee wage tracking, working hours, and trial period management.
* **Salary Rules & Structures**: Automated calculation of Basic, HRA, Allowances, PF, ESI, Professional Tax, and Deductions.
* **Monthly Payslips**: One-click compute sheet with dynamic attendance and leave sync.
* **Batch Pay Runs**: Generate and compute hundreds of employee payslips in one operation.
* **Disbursement & Accounting**: Payment tracking (Bank/Cash) and journal entry generation.
* **Printable Payslips**: Clean, employee-ready PDF salary slips.

---

## 🚀 How to Host & Go Live

### Option 1: Docker Compose (Recommended for Cloud VPS / Production)

The repository includes a ready-to-use `docker-compose.yml` for instant deployment on AWS, DigitalOcean, Linode, Hetzner, or any Linux server with Docker installed:

1. **Clone the repository on your server:**
   ```bash
   git clone https://github.com/chandramouli2812/Odoo_for_hotel_management.git
   cd Odoo_for_hotel_management
   ```

2. **Configure your passwords:**
   Copy `odoo.conf.example` to `odoo.conf` and update your database and admin passwords:
   ```bash
   cp odoo.conf.example odoo.conf
   ```

3. **Start the containers:**
   ```bash
   docker compose up -d
   ```

4. **Access Odoo:**
   Open your browser at `http://your-server-ip:8069`. Create your database and install the modules from **Apps**.

---

### Option 2: Deploy to Existing Odoo Server / Odoo.sh

1. **Clone the repository into your custom addons directory:**
   ```bash
   git clone https://github.com/chandramouli2812/Odoo_for_hotel_management.git /path/to/custom_addons
   ```

2. **Update your `odoo.conf`:**
   Add the path to your `addons_path`:
   ```ini
   addons_path = /path/to/odoo/addons,/path/to/custom_addons/custom_addons
   ```

3. **Restart Odoo service:**
   ```bash
   sudo systemctl restart odoo
   ```

4. **Install the Modules:**
   - In Odoo, activate **Developer Mode**.
   - Go to **Apps** -> **Update Apps List**.
   - Search and install:
     1. `mouli_hotels`
     2. `resort_compliance`
     3. `custom_payroll`

---

## 🔒 Security Best Practices for Production
- Never commit `odoo.conf` or `.env` containing plain-text passwords or secret keys.
- Set `list_db = False` in production once your database is created.
- Configure SSL/TLS using Nginx or Caddy as a reverse proxy on port 443.

---

## 📄 License
LGPL-3 / Proprietary (Mouli Hotels & Resorts)
