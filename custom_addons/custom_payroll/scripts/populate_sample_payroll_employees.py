import sys
import os
sys.path.insert(0, r'd:\Odoo_sample\server')

import odoo
from odoo.orm.registry import Registry
from odoo import api
from datetime import date

odoo.tools.config.parse_config(['-c', r'd:\Odoo_sample\server\odoo.conf', '-d', 'Odoo_sample'], setup_logging=False)
registry = Registry.new('Odoo_sample')

with registry.cursor() as cr:
    env = api.Environment(cr, odoo.SUPERUSER_ID, {})
    company = env['res.company'].search([], limit=1)
    struct = env.ref('custom_payroll.structure_base_monthly', raise_if_not_found=False)
    if not struct:
        struct = env['hr.payroll.structure'].search([], limit=1)

    print(f"Company: {company.name}")
    print(f"Using Structure: {struct.name if struct else 'None'}")

    # 1. Ensure Standard Departments
    dept_names = [
        "Engineering & Technology",
        "Design & Product",
        "Human Resources",
        "Finance & Accounts",
        "Sales & Marketing",
        "Operations & Support"
    ]
    dept_map = {}
    for dname in dept_names:
        dept = env['hr.department'].search([('name', '=', dname)], limit=1)
        if not dept:
            dept = env['hr.department'].create({'name': dname, 'company_id': company.id})
        dept_map[dname] = dept

    # 2. Sample Employee Profiles Data
    sample_profiles = [
        {
            "name": "Chandramouli",
            "job": "Chief Technology Officer (CTO)",
            "dept": "Engineering & Technology",
            "email": "garikinachandramouli@gmail.com",
            "phone": "+91 98480 11223",
            "wage": 85000.0,
            "bank_name": "State Bank of India",
            "acc_number": "37770722662",
            "ifsc": "SBIN0001234",
        },
        {
            "name": "Sai Ramachandra Raju",
            "job": "Lead Backend Architect",
            "dept": "Engineering & Technology",
            "email": "sai.raju@irasoft.in",
            "phone": "+91 98490 22334",
            "wage": 75000.0,
            "bank_name": "HDFC Bank",
            "acc_number": "50100458921102",
            "ifsc": "HDFC0000456",
        },
        {
            "name": "Vamsi Krishna Varma",
            "job": "Senior Full Stack Engineer",
            "dept": "Engineering & Technology",
            "email": "vamsi.varma@irasoft.in",
            "phone": "+91 98481 33445",
            "wage": 65000.0,
            "bank_name": "ICICI Bank",
            "acc_number": "002301589412",
            "ifsc": "ICIC0000023",
        },
        {
            "name": "Harsha Vardhan Reddy",
            "job": "Lead UI/UX Product Designer",
            "dept": "Design & Product",
            "email": "harsha.reddy@irasoft.in",
            "phone": "+91 98482 44556",
            "wage": 55000.0,
            "bank_name": "Axis Bank",
            "acc_number": "919010045781290",
            "ifsc": "UTIB0001045",
        },
        {
            "name": "Surya Prakash Rao",
            "job": "DevOps & Cloud Systems Engineer",
            "dept": "Engineering & Technology",
            "email": "surya.prakash@irasoft.in",
            "phone": "+91 98483 55667",
            "wage": 60000.0,
            "bank_name": "Kotak Mahindra Bank",
            "acc_number": "2811409852",
            "ifsc": "KKBK0000281",
        },
        {
            "name": "Swathi Priya Varma",
            "job": "HR & People Operations Lead",
            "dept": "Human Resources",
            "email": "swathi.varma@irasoft.in",
            "phone": "+91 98484 66778",
            "wage": 58000.0,
            "bank_name": "HDFC Bank",
            "acc_number": "50100874125890",
            "ifsc": "HDFC0000128",
        },
        {
            "name": "Lakshmi Prasanna Devi",
            "job": "Senior Financial Accountant",
            "dept": "Finance & Accounts",
            "email": "lakshmi.prasanna@irasoft.in",
            "phone": "+91 98485 77889",
            "wage": 52000.0,
            "bank_name": "State Bank of India",
            "acc_number": "38992014589",
            "ifsc": "SBIN0004821",
        },
        {
            "name": "Anusha Kumari",
            "job": "Business Development & Sales Lead",
            "dept": "Sales & Marketing",
            "email": "anusha.kumari@irasoft.in",
            "phone": "+91 98486 88990",
            "wage": 48000.0,
            "bank_name": "ICICI Bank",
            "acc_number": "014501684521",
            "ifsc": "ICIC0000145",
        },
        {
            "name": "Tarun Venkata Chowdary",
            "job": "QA Automation & Testing Engineer",
            "dept": "Engineering & Technology",
            "email": "tarun.chowdary@irasoft.in",
            "phone": "+91 98487 99001",
            "wage": 42000.0,
            "bank_name": "Axis Bank",
            "acc_number": "920010078451299",
            "ifsc": "UTIB0002145",
        },
        {
            "name": "Chaitanya Prasad Raju",
            "job": "Operations & Support Specialist",
            "dept": "Operations & Support",
            "email": "chaitanya.raju@irasoft.in",
            "phone": "+91 98488 10112",
            "wage": 40000.0,
            "bank_name": "State Bank of India",
            "acc_number": "39110458721",
            "ifsc": "SBIN0008920",
        },
    ]

    print("\nProcessing Sample Employee Profiles...")
    print("-" * 60)

    for p in sample_profiles:
        # A. Department
        dept = dept_map.get(p["dept"])

        # B. Job Position
        job = env['hr.job'].search([('name', '=', p["job"])], limit=1)
        if not job:
            job = env['hr.job'].create({
                'name': p["job"],
                'department_id': dept.id if dept else False,
                'company_id': company.id,
            })

        # C. Search or create employee
        emp = env['hr.employee'].search([('name', '=', p["name"])], limit=1)
        if not emp:
            emp = env['hr.employee'].create({
                'name': p["name"],
                'work_email': p["email"],
                'work_phone': p["phone"],
                'department_id': dept.id if dept else False,
                'job_id': job.id if job else False,
                'wage': p["wage"],
                'company_id': company.id,
            })
            print(f"[CREATED] Employee: {emp.name}")
        else:
            update_vals = {
                'work_email': p["email"],
                'work_phone': p["phone"],
                'wage': p["wage"],
            }
            if dept:
                update_vals['department_id'] = dept.id
            if job:
                update_vals['job_id'] = job.id
            emp.write(update_vals)
            print(f"[UPDATED] Employee: {emp.name} (Wage: INR {p['wage']:,.2f})")

        # D. Bank Account Setup on Work Contact Partner
        partner = emp.work_contact_id
        if partner:
            existing_bank = env['res.partner.bank'].search([
                ('partner_id', '=', partner.id),
                ('account_number', '=', p["acc_number"]),
            ], limit=1)
            if not existing_bank:
                env['res.partner.bank'].create({
                    'account_number': p["acc_number"],
                    'holder_name': emp.name,
                    'bank_name': p["bank_name"],
                    'bank_bic': p["ifsc"],
                    'partner_id': partner.id,
                    'company_id': company.id,
                })
                print(f"  -> Bank Account Added: {p['bank_name']} | Acc: {p['acc_number']} | IFSC: {p['ifsc']}")
            else:
                existing_bank.write({
                    'bank_name': p["bank_name"],
                    'bank_bic': p["ifsc"],
                    'holder_name': emp.name,
                })
                print(f"  -> Bank Account Verified: {p['bank_name']} ({p['acc_number']})")

        # E. Active Running Contract Setup
        contract = env['hr.contract'].search([
            ('employee_id', '=', emp.id),
            ('state', 'in', ('draft', 'open')),
        ], limit=1)

        if not contract:
            contract = env['hr.contract'].create({
                'name': f"CNT/2026/{emp.name.replace(' ', '_')}",
                'employee_id': emp.id,
                'department_id': dept.id if dept else False,
                'job_id': job.id if job else False,
                'wage': p["wage"],
                'struct_id': struct.id if struct else False,
                'date_start': date(2026, 1, 1),
                'state': 'open',
                'company_id': company.id,
            })
            print(f"  -> Contract Created & Running: {contract.name} (Wage: INR {contract.wage:,.2f})")
        else:
            contract.write({
                'wage': p["wage"],
                'struct_id': struct.id if struct else contract.struct_id.id,
                'state': 'open',
                'department_id': dept.id if dept else contract.department_id.id,
                'job_id': job.id if job else contract.job_id.id,
            })
            print(f"  -> Contract Updated: {contract.name} (Wage: INR {contract.wage:,.2f})")

    # Commit all changes to database
    cr.commit()
    print("-" * 60)
    print("SUCCESS: All sample employees, bank accounts, and running contracts configured!")
