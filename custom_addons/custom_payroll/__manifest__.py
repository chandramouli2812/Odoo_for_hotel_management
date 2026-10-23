# -*- coding: utf-8 -*-
{
    'name': 'Easy Payroll Management',
    'version': '20.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Simple, elegant, and powerful employee payroll processing, contracts, salary structures, payslips, and pay runs.',
    'description': """
Easy Payroll Management for Odoo
================================
A complete, easy-to-use Payroll system designed to mirror official Odoo Payroll simplicity:
* **Employee Contracts**: Track wages, working hours, trial periods, and active contract states.
* **Flexible Salary Structures & Rules**: Compute Basic Pay, HRA, Allowances, Gross, PF, Professional Tax, Deductions, and Net Salary with Fixed, Percentage, or Python code.
* **Monthly Payslips**: One-click "Compute Sheet", automatic worked days / leave calculation, and salary computation lines.
* **Batch Payslips (Pay Runs)**: Mass generate payslips for departments or the whole company in seconds.
* **Salary Disbursement**: Register payment via Bank, Cash, or Cheque with journal entries.
* **Professional Payslip Reports**: Beautiful, printable PDF Payslips ready for employees.
* **Employee Integration**: Quick smart-buttons directly on the Employee profile.
    """,
    'author': 'Custom Systems',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'hr',
        'account',
    ],
    'data': [
        'security/payroll_security.xml',
        'security/ir.access.csv',
        'data/payroll_sequence.xml',
        'data/hr_payroll_data.xml',
        'wizards/hr_payslip_employees_views.xml',
        'wizards/hr_payslip_payment_views.xml',
        'views/hr_salary_rule_category_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payroll_structure_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_employee_views.xml',
        'report/payroll_report.xml',
        'report/report_payslip_template.xml',
        'views/hr_payroll_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
