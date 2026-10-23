# -*- coding: utf-8 -*-
{
    'name': 'Resort Police & Government Compliance',
    'version': '20.0.1.0.0',
    'category': 'Industry/Hotel',
    'summary': 'Confidential Police Intimations, FRRO/Form C, FIR Tracker, Security & Law Enforcement Compliance',
    'description': """
Resort Police & Government Compliance Module
=============================================
Dedicated compliance management for Indian and international resorts & hotels:

Features:
---------
* Guest / Visitor Police Reporting & Daily Intimations
* Foreign Guest / Bureau of Immigration (BoI) FRRO Form C Tracker
* Incident & FIR Reference Register (Theft, Disputes, Accidents, Property Damage)
* Police Visit Register (Official log of law enforcement visits & inquiries)
* Resort Security Logs (Visitor Register, Vehicle Entry/Exit, Patrol & CCTV)
* Police Submission Workflow (Draft -> Pending Review -> Ready -> Submitted -> Acknowledged -> Closed)
* Strict Role-Based Access Control (Sensitive records hidden from general hotel staff)
* Official Printable QWeb PDF Reports for Police Station & FRRO Submissions
    """,
    'author': 'Mouli Hotels & Resorts',
    'depends': [
        'base',
        'mail',
        'contacts',
        'mouli_hotels',
    ],
    'data': [
        'security/resort_compliance_security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'wizards/compliance_police_submission_wizard_views.xml',
        'views/compliance_guest_report_views.xml',
        'views/compliance_foreign_guest_views.xml',
        'views/compliance_incident_views.xml',
        'views/compliance_police_visit_views.xml',
        'views/compliance_security_log_views.xml',
        'views/hotel_reservation_compliance_views.xml',
        'report/compliance_report_templates.xml',
        'report/compliance_reports.xml',
        'views/compliance_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
