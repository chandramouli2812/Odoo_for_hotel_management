# -*- coding: utf-8 -*-
{
    'name': 'Mouli Hotels Management',
    'version': '20.0.1.0.0',
    'category': 'Industry/Hotel',
    'summary': 'Comprehensive Hotel & Resort PMS: Reservations, Rooms, Folios, Housekeeping & Operations',
    'description': """
Mouli Hotels Management System
==============================
Connects Hotel Operations, Reservations, Housekeeping, Guest Folios, Billing, POS, and Inventory.

Features:
---------
* Property & Multi-building & Floor Management
* Room Types & Amenity Management
* Dynamic Room Status (Occupancy, Housekeeping, Maintenance)
* Booking & Reservation Engine with double-booking prevention
* Front Desk: Check-in / Check-out workflows
* Guest Stay Folio & Integrated Invoice Generation
* Housekeeping Task Management & Room Turnaround
* Guest Profiles & History Extension (res.partner)
* POS Restaurant & Maintenance Integration
    """,
    'author': 'Mouli Hotels',
    'depends': [
        'base',
        'mail',
        'contacts',
        'account',
        'hr',
        'point_of_sale',
        'stock',
        'maintenance',
        'website',
        'crm',
    ],
    'data': [
        'security/hotel_security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'data/hotel_breakfast_data.xml',
        'data/hotel_website_menu.xml',
        'views/hotel_property_views.xml',
        'views/hotel_room_views.xml',
        'views/res_partner_views.xml',
        'views/hotel_reservation_views.xml',
        'views/hotel_folio_views.xml',
        'views/hotel_housekeeping_views.xml',
        'wizards/hotel_quick_checkout_views.xml',
        'views/hotel_folio_report.xml',
        'views/hotel_breakfast_service_views.xml',
        'views/hotel_operational_reports.xml',
        'views/hotel_operational_reports_template.xml',
        'views/hotel_reservation_report_views.xml',
        'views/hotel_daily_flash_report_views.xml',
        'views/hotel_reporting_views.xml',
        'views/hotel_flash_report_template.xml',
        'views/hotel_website_templates.xml',
        'views/hotel_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mouli_hotels/static/src/tape_chart/hotel_tape_chart.scss',
            'mouli_hotels/static/src/tape_chart/hotel_tape_chart.js',
            'mouli_hotels/static/src/tape_chart/hotel_tape_chart.xml',
        ],
        'web.assets_frontend': [
            'mouli_hotels/static/src/css/hotel_website.css',
            'mouli_hotels/static/src/js/hotel_website.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
