# -*- coding: utf-8 -*-
"""
Coastal Andhra Pradesh Demo Data Generator for RB Resorts
Populates realistic, culturally authentic employees, assignments, bookings,
breakfast covers, and compliance records for client sales demonstrations.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, r'D:\Odoo_sample\server')
import odoo
from odoo.tools import config
config.parse_config(['-c', r'D:\Odoo_sample\server\odoo.conf'])
from odoo.modules.registry import Registry

def populate_ap_demo_data():
    registry = Registry('Odoo_sample')
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        now = datetime.now()
        today = now.date()

        print("=" * 70)
        print("POPLUATING COASTAL ANDHRA PRADESH DEMO DATA FOR RB RESORTS")
        print("=" * 70)

        # 1. GET RB RESORTS PROPERTY
        Property = env['hotel.property']
        rb_resort = Property.search([('name', 'ilike', 'RB Resorts')], limit=1)
        if not rb_resort:
            rb_resort = Property.create({
                'name': 'RB Luxury Beach Resort & Spa',
                'code': 'RBR',
                'street': 'Beach Road, Rushikonda - Bheemili Marine Drive',
                'city': 'Visakhapatnam',
                'state_id': env['res.country.state'].search([('name', 'ilike', 'Andhra Pradesh')], limit=1).id,
                'country_id': env['res.country'].search([('code', '=', 'IN')], limit=1).id,
                'phone': '+91 891 285 4500',
                'email': 'reservations@rbresorts.in',
                'website': 'https://www.rbresorts.in',
            })
        print(f"-> Target Property: {rb_resort.name} (ID: {rb_resort.id})")

        # 2. DEPARTMENTS
        Department = env['hr.department']
        dept_names = [
            'Executive Management',
            'Front Office & Concierge',
            'Housekeeping & Guest Care',
            'Food & Beverage (Culinary)',
            'Security & Statutory Compliance',
        ]
        depts = {}
        for d_name in dept_names:
            dept = Department.search([('name', '=', d_name)], limit=1)
            if not dept:
                dept = Department.create({'name': d_name})
            depts[d_name] = dept
        print(f"-> Departments ready: {list(depts.keys())}")

        # 3. EMPLOYEES: COASTAL ANDHRA BOYS & GIRLS
        Employee = env['hr.employee']
        User = env['res.users']

        # List of 14 authentic Coastal AP staff
        employee_specs = [
            # --- BOYS ---
            {
                'name': 'Sai Ramachandra Raju',
                'gender_tag': 'Boy',
                'origin': 'Bhimavaram / Visakhapatnam',
                'job_title': 'Resort General Manager',
                'dept': 'Executive Management',
                'email': 'sai.raju@rbresorts.in',
                'phone': '+91 98480 12345',
                'is_user': True,
            },
            {
                'name': 'Vamsi Krishna Varma',
                'gender_tag': 'Boy',
                'origin': 'Kakinada',
                'job_title': 'Front Desk Duty Manager',
                'dept': 'Front Office & Concierge',
                'email': 'vamsi.varma@rbresorts.in',
                'phone': '+91 94401 23456',
                'is_user': True,
            },
            {
                'name': 'Tarun Venkata Chowdary',
                'gender_tag': 'Boy',
                'origin': 'Vijayawada',
                'job_title': 'Front Office Executive & Cashier',
                'dept': 'Front Office & Concierge',
                'email': 'tarun.chowdary@rbresorts.in',
                'phone': '+91 99890 34567',
                'is_user': False,
            },
            {
                'name': 'Chaitanya Prasad Raju',
                'gender_tag': 'Boy',
                'origin': 'Bhimavaram',
                'job_title': 'Executive Housekeeping Supervisor',
                'dept': 'Housekeeping & Guest Care',
                'email': 'chaitanya.raju@rbresorts.in',
                'phone': '+91 98492 45678',
                'is_user': False,
            },
            {
                'name': 'Harsha Vardhan Reddy',
                'gender_tag': 'Boy',
                'origin': 'Guntur',
                'job_title': 'Senior Room Attendant',
                'dept': 'Housekeeping & Guest Care',
                'email': 'harsha.reddy@rbresorts.in',
                'phone': '+91 94901 56789',
                'is_user': False,
            },
            {
                'name': 'Surya Prakash Rao',
                'gender_tag': 'Boy',
                'origin': 'Rajahmundry',
                'job_title': 'Chief Security Officer & Compliance In-Charge',
                'dept': 'Security & Statutory Compliance',
                'email': 'surya.prakash@rbresorts.in',
                'phone': '+91 98660 67890',
                'is_user': True,
            },
            {
                'name': 'Pavan Kalyan Varma',
                'gender_tag': 'Boy',
                'origin': 'Amalapuram (Konaseema)',
                'job_title': 'F&B Restaurant Captain & Breakfast Host',
                'dept': 'Food & Beverage (Culinary)',
                'email': 'pavan.kalyan@rbresorts.in',
                'phone': '+91 97012 78901',
                'is_user': True,
            },
            # --- GIRLS ---
            {
                'name': 'Swathi Priya Varma',
                'gender_tag': 'Girl',
                'origin': 'Visakhapatnam',
                'job_title': 'Guest Relations Manager & VIP Concierge',
                'dept': 'Front Office & Concierge',
                'email': 'swathi.varma@rbresorts.in',
                'phone': '+91 98485 23456',
                'is_user': True,
            },
            {
                'name': 'Lakshmi Prasanna Devi',
                'gender_tag': 'Girl',
                'origin': 'Rajahmundry',
                'job_title': 'Front Desk Supervisor & Night Auditor',
                'dept': 'Front Office & Concierge',
                'email': 'lakshmi.prasanna@rbresorts.in',
                'phone': '+91 94405 34567',
                'is_user': False,
            },
            {
                'name': 'Divya Teja Chowdary',
                'gender_tag': 'Girl',
                'origin': 'Vijayawada',
                'job_title': 'Executive Housekeeping Inspector',
                'dept': 'Housekeeping & Guest Care',
                'email': 'divya.teja@rbresorts.in',
                'phone': '+91 99895 45678',
                'is_user': False,
            },
            {
                'name': 'Sravani Durga Raju',
                'gender_tag': 'Girl',
                'origin': 'Kakinada',
                'job_title': 'Room Turnaround & Linen Specialist',
                'dept': 'Housekeeping & Guest Care',
                'email': 'sravani.raju@rbresorts.in',
                'phone': '+91 98495 56789',
                'is_user': False,
            },
            {
                'name': 'Anusha Kumari',
                'gender_tag': 'Girl',
                'origin': 'Guntur',
                'job_title': 'Front Desk Cashier & Accounts Assistant',
                'dept': 'Front Office & Concierge',
                'email': 'anusha.kumari@rbresorts.in',
                'phone': '+91 94905 67890',
                'is_user': False,
            },
            {
                'name': 'Bhavani Shankari',
                'gender_tag': 'Girl',
                'origin': 'Amalapuram (Konaseema)',
                'job_title': 'Executive Sous Chef & Breakfast Kitchen Lead',
                'dept': 'Food & Beverage (Culinary)',
                'email': 'bhavani.shankari@rbresorts.in',
                'phone': '+91 98665 78901',
                'is_user': False,
            },
            {
                'name': 'Yamini Durga Varma',
                'gender_tag': 'Girl',
                'origin': 'Bheemili Marine Zone',
                'job_title': 'Resort Gate Security & Paperless e-Pass Officer',
                'dept': 'Security & Statutory Compliance',
                'email': 'yamini.durga@rbresorts.in',
                'phone': '+91 97015 89012',
                'is_user': False,
            },
        ]

        staff_map = {}
        users_map = {}

        for spec in employee_specs:
            emp = Employee.search([('name', '=', spec['name'])], limit=1)
            emp_vals = {
                'name': spec['name'],
                'job_title': spec['job_title'],
                'department_id': depts[spec['dept']].id,
                'work_email': spec['email'],
                'work_phone': spec['phone'],
                'company_id': env.company.id,
            }
            if not emp:
                emp = Employee.create(emp_vals)
            else:
                emp.write(emp_vals)
            staff_map[spec['name']] = emp

            # If user access needed
            if spec['is_user']:
                usr = User.search([('login', '=', spec['email'])], limit=1)
                if not usr:
                    usr = User.create({
                        'name': spec['name'],
                        'login': spec['email'],
                        'email': spec['email'],
                        'company_id': env.company.id,
                        'company_ids': [(6, 0, [env.company.id])],
                    })
                emp.user_id = usr.id
                users_map[spec['name']] = usr

        print(f"-> Loaded {len(staff_map)} Coastal Andhra employees successfully!")

        # Set Manager Hierarchy
        gm = staff_map['Sai Ramachandra Raju']
        for name, emp in staff_map.items():
            if name != 'Sai Ramachandra Raju':
                emp.parent_id = gm.id

        # 4. HOUSEKEEPING TASKS ASSIGNED TO EMPLOYEES
        Housekeeping = env['hotel.housekeeping.task']
        Room = env['hotel.room']

        # Get rooms in RB Resorts
        r101 = Room.search([('property_id', '=', rb_resort.id), ('room_number', '=', '101')], limit=1)
        r102 = Room.search([('property_id', '=', rb_resort.id), ('room_number', '=', '102')], limit=1)
        r104 = Room.search([('property_id', '=', rb_resort.id), ('room_number', '=', '104')], limit=1)
        r201 = Room.search([('property_id', '=', rb_resort.id), ('room_number', '=', '201')], limit=1)
        r204 = Room.search([('property_id', '=', rb_resort.id), ('room_number', '=', '204')], limit=1)
        r302 = Room.search([('property_id', '=', rb_resort.id), ('room_number', '=', '302')], limit=1)
        r_p01 = Room.search([('property_id', '=', rb_resort.id), ('room_number', '=', 'P01')], limit=1)
        r_v01 = Room.search([('property_id', '=', rb_resort.id), ('room_number', '=', 'V01')], limit=1)

        hk_tasks_data = [
            {
                'room': r_v01,
                'task_type': 'checkout_clean',
                'state': 'in_progress',
                'priority': '3',
                'assignee': staff_map['Harsha Vardhan Reddy'],
                'notes': 'Urgent turnaround for Diamond VIP Guest arrival today. Extra sea-facing balcony sanitization.',
            },
            {
                'room': r102,
                'task_type': 'stayover_clean',
                'state': 'in_progress',
                'priority': '1',
                'assignee': staff_map['Sravani Durga Raju'],
                'notes': 'Daily linen change, organic herbal shampoo restocking, and baby crib dusting.',
            },
            {
                'room': r201,
                'task_type': 'checkout_clean',
                'state': 'draft',
                'priority': '2',
                'assignee': staff_map['Chaitanya Prasad Raju'],
                'notes': 'Checkout departure scheduled today at 12:00 PM. High-priority turnaround for evening arrival.',
            },
            {
                'room': r_p01,
                'task_type': 'deep_clean',
                'state': 'inspected',
                'priority': '3',
                'assignee': staff_map['Divya Teja Chowdary'],
                'notes': 'Penthouse luxury inspection completed: Private Jacuzzi sanitized, fresh orchids placed, mini-bar restocked. Approved by Divya Teja Chowdary.',
            },
            {
                'room': r101,
                'task_type': 'stayover_clean',
                'state': 'done',
                'priority': '2',
                'assignee': staff_map['Harsha Vardhan Reddy'],
                'notes': 'German guest stayover clean completed. Awaiting supervisor inspection sign-off.',
            },
            {
                'room': r302,
                'task_type': 'turndown',
                'state': 'draft',
                'priority': '1',
                'assignee': staff_map['Sravani Durga Raju'],
                'notes': 'Vacant room fragrance touch-up and fresh water bottle replenishment.',
            },
        ]

        for hk_item in hk_tasks_data:
            if hk_item['room']:
                task = Housekeeping.search([
                    ('room_id', '=', hk_item['room'].id),
                    ('task_type', '=', hk_item['task_type']),
                    ('scheduled_date', '=', today),
                ], limit=1)
                t_vals = {
                    'room_id': hk_item['room'].id,
                    'property_id': rb_resort.id,
                    'task_type': hk_item['task_type'],
                    'state': hk_item['state'],
                    'priority': hk_item['priority'],
                    'assigned_to_id': hk_item['assignee'].id,
                    'scheduled_date': today,
                    'notes': hk_item['notes'],
                }
                if not task:
                    Housekeeping.create(t_vals)
                else:
                    task.write(t_vals)
        print("-> Housekeeping tasks assigned to Coastal AP team successfully!")

        # 5. GUEST PROFILES FOR SALES DEMO
        Partner = env['res.partner']
        Country = env['res.country']
        india = Country.search([('code', '=', 'IN')], limit=1)
        germany = Country.search([('code', '=', 'DE')], limit=1)

        guests_data = [
            {
                'name': 'Gokaraju Venkata Rama Raju',
                'email': 'gvr.raju@rajutech.com',
                'phone': '+91 98490 88888',
                'city': 'Bhimavaram',
                'country_id': india.id,
                'is_hotel_guest': True,
                'vip_status': 'platinum',
                'guest_notes': 'Industrialist & Tech Chairman. Prefers sea-view sunrise villa, fresh tender coconut on arrival.',
            },
            {
                'name': 'Muppala Ranganayakamma',
                'email': 'm.ranganayaki@vizagarts.org',
                'phone': '+91 94401 77777',
                'city': 'Visakhapatnam',
                'country_id': india.id,
                'is_hotel_guest': True,
                'vip_status': 'platinum',
                'guest_notes': 'Celebrity Film Producer & Author. Absolute privacy requested. Prefers coastal Andhra bamboo seafood dining.',
            },
            {
                'name': 'Koganti Tarun Chowdary',
                'email': 'tarun@kakinadaportexports.com',
                'phone': '+91 99890 66666',
                'city': 'Kakinada',
                'country_id': india.id,
                'is_hotel_guest': True,
                'vip_status': 'gold',
                'guest_notes': 'Port Shipping Magnate. High-frequency corporate traveler. Express checkout required.',
            },
            {
                'name': 'Alluri Sitarama Varma',
                'email': 'asrv.varma@tanukusugars.in',
                'phone': '+91 98481 55555',
                'city': 'Tanuku',
                'country_id': india.id,
                'is_hotel_guest': True,
                'vip_status': 'silver',
                'guest_notes': 'Family holiday. Requires extra bed and child high chair.',
            },
            {
                'name': 'Dr. Heinrich Weber',
                'email': 'h.weber@ocean-marine.de',
                'phone': '+49 171 8923456',
                'city': 'Hamburg',
                'country_id': germany.id,
                'is_hotel_guest': True,
                'vip_status': 'gold',
                'guest_notes': 'German Oceanographic Researcher. High-speed Wi-Fi essential for satellite data uplink.',
            },
        ]

        demo_guests = {}
        for g_spec in guests_data:
            gst = Partner.search([('email', '=', g_spec['email'])], limit=1)
            if not gst:
                gst = Partner.create(g_spec)
            else:
                gst.write(g_spec)
            demo_guests[g_spec['name']] = gst
        print(f"-> Demo Guests created: {len(demo_guests)}")

        # 6. BOOKINGS FOR SALES DEMO
        Reservation = env['hotel.reservation']
        Folio = env['hotel.folio']
        FolioLine = env['hotel.folio.line']
        FolioPayment = env['hotel.folio.payment']
        RoomType = env['hotel.room.type']

        villa_type = RoomType.search([('name', 'ilike', 'Villa')], limit=1)
        penthouse_type = RoomType.search([('name', 'ilike', 'Penthouse')], limit=1)
        suite_type = RoomType.search([('name', 'ilike', 'Suite')], limit=1)
        deluxe_type = RoomType.search([('name', 'ilike', 'Deluxe')], limit=1)

        # Mark any past expired reservations on RB Resorts as checked out
        past_expired = Reservation.search([
            ('property_id', '=', rb_resort.id),
            ('state', 'in', ('confirmed', 'check_in')),
            ('check_out', '<=', datetime.combine(today, datetime.strptime("00:00:00", "%H:%M:%S").time())),
        ])
        for p_res in past_expired:
            p_res.state = 'check_out'

        # SPECIFICATIONS FOR 5 TARGET DEMO BOOKINGS
        booking_plans = [
            # 1. TODAY'S ARRIVAL: Diamond VIP G.V.R. Raju (Expected Check-in today at 14:00)
            {
                'guest': demo_guests['Gokaraju Venkata Rama Raju'],
                'room': r_v01,
                'room_type': villa_type,
                'check_in': datetime.combine(today, datetime.strptime("14:00:00", "%H:%M:%S").time()),
                'check_out': datetime.combine(today + timedelta(days=4), datetime.strptime("11:00:00", "%H:%M:%S").time()),
                'state': 'confirmed', # READY FOR 1-CLICK CHECK-IN DEMO!
                'adults': 2,
                'children': 0,
                'meal_plan': 'ap',
                'rate': 18000.0,
                'advance': 36000.0,
                'advance_method': 'upi',
                'is_vip': True,
                'vip_status': 'platinum',
                'dietary': 'Strict Vegetarian • Organic Almond Milk & Herbal Green Tea',
                'notes': 'Diamond VIP Client. Arrange traditional Visakhapatnam poornam boorelu & tender coconut welcome drink.',
                'extra_charges': [],
                'extra_payments': [],
            },
            # 2. IN-HOUSE VIP STAY: Platinum VIP M. Ranganayakamma (Active in Penthouse P01)
            {
                'guest': demo_guests['Muppala Ranganayakamma'],
                'room': r_p01,
                'room_type': penthouse_type,
                'check_in': datetime.combine(today - timedelta(days=2), datetime.strptime("12:00:00", "%H:%M:%S").time()),
                'check_out': datetime.combine(today + timedelta(days=3), datetime.strptime("11:00:00", "%H:%M:%S").time()),
                'state': 'check_in', # IN-HOUSE!
                'adults': 2,
                'children': 0,
                'meal_plan': 'map',
                'rate': 25000.0,
                'advance': 50000.0,
                'advance_method': 'bank',
                'is_vip': True,
                'vip_status': 'platinum',
                'dietary': 'Coastal Andhra Seafood Specialties (Royyala Vepudu, Bamboo Biryani)',
                'notes': 'Platinum VIP Guest. 24/7 dedicated butler service assigned to Pavan Kalyan Varma.',
                'extra_charges': [
                    ('Baywatch Coastal Restaurant Dinner (Royyala Vepudu, Bamboo Biryani)', 'restaurant', 1, 8500.0),
                    ('Ayurvedic Abhyanga Full-Body Herbal Spa Therapy (2 Pax)', 'spa', 2, 6500.0),
                    ('Presidential In-Room Bar & Artisan Nespresso Refills', 'bar', 1, 3200.0),
                ],
                'extra_payments': [
                    ('Mid-Stay Dining Payment (UPI - PhonePe)', 10000.0, 'upi', 'UPI-PHN-2026-9921')
                ],
            },
            # 3. TODAY'S DUE-OUT DEPARTURE: Gold VIP K. Tarun Chowdary (Checking out today with balance due!)
            {
                'guest': demo_guests['Koganti Tarun Chowdary'],
                'room': r201,
                'room_type': suite_type,
                'check_in': datetime.combine(today - timedelta(days=1), datetime.strptime("12:00:00", "%H:%M:%S").time()),
                'check_out': datetime.combine(today, datetime.strptime("11:30:00", "%H:%M:%S").time()),
                'state': 'check_in', # DUE OUT TODAY! READY FOR 1-CLICK QUICK CHECKOUT DEMO!
                'adults': 1,
                'children': 0,
                'meal_plan': 'cp',
                'rate': 6500.0,
                'advance': 4000.0,
                'advance_method': 'card',
                'is_vip': True,
                'vip_status': 'gold',
                'dietary': 'Executive Continental Breakfast & Black Americano',
                'notes': 'Kakinada Port shipping meeting. Fast checkout bill requested by Tarun Venkata Chowdary at front desk.',
                'extra_charges': [
                    ('Executive Boardroom Half-Day Conference Booking', 'other', 1, 4500.0),
                    ('Express Suit Steam Ironing & Dry Clean', 'laundry', 3, 1200.0),
                    ('Room Service Midnight Club Sandwich & Fresh Lime', 'restaurant', 1, 950.0),
                ],
                'extra_payments': [], # Balance remains due for the wizard checkout demo!
            },
            # 4. FAMILY VACATION IN-HOUSE: Alluri Sitarama Varma (Deluxe Room 102)
            {
                'guest': demo_guests['Alluri Sitarama Varma'],
                'room': r102,
                'room_type': deluxe_type,
                'check_in': datetime.combine(today - timedelta(days=1), datetime.strptime("14:00:00", "%H:%M:%S").time()),
                'check_out': datetime.combine(today + timedelta(days=2), datetime.strptime("11:00:00", "%H:%M:%S").time()),
                'state': 'check_in', # IN-HOUSE!
                'adults': 2,
                'children': 1,
                'meal_plan': 'cp',
                'rate': 4500.0,
                'advance': 9000.0,
                'advance_method': 'upi',
                'is_vip': True,
                'vip_status': 'silver',
                'dietary': 'Pure Vegetarian • Jain Style Breakfast for Family',
                'notes': 'Family holiday from Tanuku. Extra mattress and pool towels provided.',
                'extra_charges': [
                    ('Beach Shack Tender Coconut & Andhra Mirchi Bajji Platters', 'restaurant', 1, 1450.0),
                    ('Children Swimming Pool Kit & Inflatables', 'other', 1, 850.0),
                ],
                'extra_payments': [],
            },
            # 5. FOREIGN LUXURY RESEARCHER: Dr. Heinrich Weber (Deluxe Room 101)
            {
                'guest': demo_guests['Dr. Heinrich Weber'],
                'room': r101,
                'room_type': deluxe_type,
                'check_in': datetime.combine(today - timedelta(days=1), datetime.strptime("18:00:00", "%H:%M:%S").time()),
                'check_out': datetime.combine(today + timedelta(days=5), datetime.strptime("10:00:00", "%H:%M:%S").time()),
                'state': 'check_in', # IN-HOUSE! LINKED TO FORM C & POLICE INTIMATION
                'adults': 1,
                'children': 0,
                'meal_plan': 'ep',
                'rate': 4500.0,
                'advance': 15000.0,
                'advance_method': 'card',
                'is_vip': True,
                'vip_status': 'gold',
                'dietary': 'Gluten-Free Muesli, Scrambled Eggs & Espresso',
                'notes': 'German Oceanographer. Passport & Form C completed with Visakhapatnam FRRO.',
                'extra_charges': [
                    ('Airport Luxury Sedan Pickup (Visakhapatnam Airport - VTZ)', 'other', 1, 2200.0),
                    ('Laundry Service (Linens & Shirts)', 'laundry', 1, 1100.0),
                ],
                'extra_payments': [],
            },
        ]

        active_reservations = []

        for b_spec in booking_plans:
            # Check existing
            res = Reservation.search([
                ('guest_id', '=', b_spec['guest'].id),
                ('room_id', '=', b_spec['room'].id),
                ('state', '=', b_spec['state']),
            ], limit=1)

            total_stay_nights = (b_spec['check_out'].date() - b_spec['check_in'].date()).days or 1

            res_vals = {
                'guest_id': b_spec['guest'].id,
                'property_id': rb_resort.id,
                'room_type_id': b_spec['room_type'].id if b_spec['room_type'] else b_spec['room'].room_type_id.id,
                'room_id': b_spec['room'].id,
                'check_in': b_spec['check_in'],
                'check_out': b_spec['check_out'],
                'adults': b_spec['adults'],
                'children': b_spec['children'],
                'rate_per_night': b_spec['rate'],
                'advance_payment': b_spec['advance'],
                'advance_payment_method': b_spec['advance_method'],
                'advance_payment_ref': f"ADV-{b_spec['advance_method'].upper()}-RB2026",
                'state': b_spec['state'],
                'meal_plan': b_spec['meal_plan'],
                'dietary_notes': b_spec['dietary'],
                'notes': b_spec['notes'],
                'booking_source': 'direct',
            }

            if not res:
                res = Reservation.create(res_vals)
            else:
                res.write(res_vals)
            active_reservations.append((res, b_spec))

            # Folio management
            folio = Folio.search([('reservation_id', '=', res.id)], limit=1)
            if not folio:
                folio = Folio.create({
                    'reservation_id': res.id,
                    'guest_id': b_spec['guest'].id,
                    'room_id': b_spec['room'].id,
                    'property_id': rb_resort.id,
                    'date_order': b_spec['check_in'],
                })
                res.folio_id = folio.id

                # Room Stay Charge Line
                FolioLine.create({
                    'folio_id': folio.id,
                    'name': f"Resort Stay Accommodation: {b_spec['room'].name} ({total_stay_nights} Nights)",
                    'service_type': 'room',
                    'quantity': total_stay_nights,
                    'price_unit': b_spec['rate'],
                })

                # Advance Payment
                if b_spec['advance'] > 0:
                    FolioPayment.create({
                        'folio_id': folio.id,
                        'name': f"Advance Booking Deposit ({b_spec['advance_method'].upper()})",
                        'amount': b_spec['advance'],
                        'payment_method': b_spec['advance_method'],
                        'reference': f"ADV-{b_spec['advance_method'].upper()}-{res.id}",
                        'is_advance': True,
                        'payment_date': b_spec['check_in'],
                    })

                # Extra Service Charges
                for line_title, stype, qty, price in b_spec['extra_charges']:
                    FolioLine.create({
                        'folio_id': folio.id,
                        'name': line_title,
                        'service_type': stype,
                        'quantity': qty,
                        'price_unit': price,
                    })

                # Extra Payments
                for p_name, p_amt, p_mode, p_ref in b_spec['extra_payments']:
                    FolioPayment.create({
                        'folio_id': folio.id,
                        'name': p_name,
                        'amount': p_amt,
                        'payment_method': p_mode,
                        'reference': p_ref,
                        'payment_date': now,
                    })

            # Sync Room State
            if b_spec['state'] == 'check_in':
                b_spec['room'].write({
                    'occupancy_status': 'occupied',
                    'current_reservation_id': res.id,
                })
            elif b_spec['state'] == 'confirmed':
                b_spec['room'].write({
                    'occupancy_status': 'reserved',
                })

        print(f"-> Created {len(active_reservations)} high-impact demo reservations for RB Resorts!")

        # 7. BREAKFAST ATTENDANCE FOR TODAY (COVERS ROSTER)
        Breakfast = env['hotel.breakfast.service']
        BreakfastLine = env['hotel.breakfast.service.line']
        Item = env['hotel.breakfast.item']

        dosa_item = Item.search([('name', 'ilike', 'Dosa')], limit=1)
        idli_item = Item.search([('name', 'ilike', 'Idli')], limit=1)
        omelette_item = Item.search([('name', 'ilike', 'Omelette')], limit=1)
        croissant_item = Item.search([('name', 'ilike', 'Croissant')], limit=1)
        pancake_item = Item.search([('name', 'ilike', 'Pancake')], limit=1)

        # Create Coastal AP Specialties if missing
        pesarattu = Item.search([('name', 'ilike', 'Pesarattu')], limit=1)
        if not pesarattu:
            pesarattu = Item.create({
                'name': 'Andhra MLA Pesarattu with Upma & Ginger Allam Pachadi',
                'category': 'indian',
                'dietary_type': 'veg',
                'is_buffet_standard': True,
                'description': 'Crispy green gram crepe stuffed with savoury semolina upma and piquant ginger chutney',
            })

        filter_coffee = Item.search([('name', 'ilike', 'Filter Coffee')], limit=1)
        if not filter_coffee:
            filter_coffee = Item.create({
                'name': 'Traditional Kumbakonam Degree / South Indian Filter Coffee',
                'category': 'beverages',
                'dietary_type': 'veg',
                'is_buffet_standard': True,
                'description': 'Freshly brewed chicory dark roast decoction frothed with boiling whole milk in brass davarah',
            })

        bf_manifest_specs = [
            # Penthouse VIP: Muppala Ranganayakamma (Served in Room)
            {
                'reservation': active_reservations[1][0],
                'room': r_p01,
                'guest': demo_guests['Muppala Ranganayakamma'],
                'adults': 2,
                'children': 0,
                'total_covers': 2,
                'entitlement': 'included',
                'status': 'served',
                'served_time': datetime.combine(today, datetime.strptime("08:15:00", "%H:%M:%S").time()),
                'outlet': 'room_service',
                'dietary_notes': 'Coastal Andhra Pesarattu, Filter Coffee, Fresh Watermelon Juice',
                'items': [(pesarattu, 2, 'Crispy with ginger chutney'), (filter_coffee, 2, 'Strong decoction, low sugar')],
            },
            # Suite VIP: Koganti Tarun Chowdary (Room Tray Delivered)
            {
                'reservation': active_reservations[2][0],
                'room': r201,
                'guest': demo_guests['Koganti Tarun Chowdary'],
                'adults': 1,
                'children': 0,
                'total_covers': 1,
                'entitlement': 'included',
                'status': 'room_service',
                'served_time': datetime.combine(today, datetime.strptime("08:45:00", "%H:%M:%S").time()),
                'outlet': 'room_service',
                'dietary_notes': 'Executive Breakfast Tray • Black Coffee & Cheese Omelette',
                'items': [(omelette_item or pesarattu, 1, 'Egg white only, extra pepper'), (croissant_item or pesarattu, 1, 'Warm')],
            },
            # Deluxe 102: Alluri Sitarama Varma (Buffet Restaurant Served)
            {
                'reservation': active_reservations[3][0],
                'room': r102,
                'guest': demo_guests['Alluri Sitarama Varma'],
                'adults': 2,
                'children': 1,
                'total_covers': 3,
                'entitlement': 'included',
                'status': 'served',
                'served_time': datetime.combine(today, datetime.strptime("09:10:00", "%H:%M:%S").time()),
                'outlet': 'main_restaurant',
                'dietary_notes': 'Pure Vegetarian Family Buffet • Ghee Dosa & Sweet Lassi for child',
                'items': [(dosa_item or pesarattu, 2, 'Golden Ghee Roast'), (idli_item or pesarattu, 1, 'Soft Ghee Idli with Sambar')],
            },
            # Deluxe 101: Dr. Heinrich Weber (Pending Guest Arrival)
            {
                'reservation': active_reservations[4][0],
                'room': r101,
                'guest': demo_guests['Dr. Heinrich Weber'],
                'adults': 1,
                'children': 0,
                'total_covers': 1,
                'entitlement': 'chargeable',
                'status': 'pending',
                'served_time': False,
                'outlet': 'main_restaurant',
                'dietary_notes': 'Continental Platter • Gluten-free Toast & Double Espresso',
                'items': [(croissant_item or pesarattu, 1, 'With orange marmalade')],
            },
        ]

        for bf_s in bf_manifest_specs:
            bf_rec = Breakfast.search([
                ('reservation_id', '=', bf_s['reservation'].id),
                ('date', '=', today),
            ], limit=1)
            bf_vals = {
                'date': today,
                'reservation_id': bf_s['reservation'].id,
                'adults': bf_s['adults'],
                'children': bf_s['children'],
                'meal_plan': bf_s['reservation'].meal_plan,
                'breakfast_entitlement': bf_s['entitlement'],
                'service_status': bf_s['status'],
                'served_time': bf_s['served_time'],
                'outlet': bf_s['outlet'],
                'dietary_notes': bf_s['dietary_notes'],
            }
            if not bf_rec:
                bf_rec = Breakfast.create(bf_vals)
                for item_obj, qty, it_notes in bf_s['items']:
                    if item_obj:
                        BreakfastLine.create({
                            'service_id': bf_rec.id,
                            'item_id': item_obj.id,
                            'quantity': qty,
                            'notes': it_notes,
                        })
            else:
                bf_rec.write(bf_vals)

        print("-> Daily Breakfast covers roster initialized with Coastal Andhra delicacies!")

        # 8. RESORT COMPLIANCE DEMO RECORDS
        ForeignGuest = env['compliance.foreign.guest']
        GuestReport = env['compliance.guest.report']
        PoliceVisit = env['compliance.police.visit']
        SecurityLog = env['compliance.security.log']

        dr_weber_res = active_reservations[4][0]
        dr_weber_partner = demo_guests['Dr. Heinrich Weber']

        # Foreign Guest Form C
        fg = ForeignGuest.search([('guest_id', '=', dr_weber_partner.id)], limit=1)
        fg_vals = {
            'guest_id': dr_weber_partner.id,
            'reservation_id': dr_weber_res.id,
            'room_id': r101.id,
            'property_id': rb_resort.id,
            'nationality_id': germany.id,
            'passport_number': 'C4L990188',
            'passport_country_id': germany.id,
            'passport_expiry_date': today + timedelta(days=730),
            'visa_number': 'IN-VISA-994108',
            'visa_type': 'business',
            'visa_valid_until': today + timedelta(days=90),
            'arrival_in_india_date': today - timedelta(days=2),
            'arrival_at_hotel': now - timedelta(days=1),
            'port_of_entry': 'Visakhapatnam Seaport / Airport',
            'phone_in_india': '+91 94401 99999',
            'emergency_contact': '+49 40 428380 (University of Hamburg Oceanography)',
            'purpose_of_visit': 'business',
            'next_destination': 'Chennai Port / Research Vessel',
            'state': 'submitted',
            'frro_portal_status': 'submitted',
            'frro_ack_number': 'BOI-2026-VIZAG-0941',
            'doc_passport_copy': True,
            'doc_visa_copy': True,
            'doc_entry_stamp': True,
            'doc_photo': True,
        }
        if not fg:
            ForeignGuest.create(fg_vals)
        else:
            fg.write(fg_vals)

        # Police Guest Intimation
        gr = GuestReport.search([('guest_id', '=', dr_weber_partner.id)], limit=1)
        gr_vals = {
            'guest_id': dr_weber_partner.id,
            'reservation_id': dr_weber_res.id,
            'room_id': r101.id,
            'property_id': rb_resort.id,
            'nationality_id': germany.id,
            'reporting_type': 'foreign',
            'id_type': 'passport',
            'id_number': 'C4L990188',
            'guest_phone': '+91 94401 99999',
            'guest_email': 'h.weber@ocean-marine.de',
            'permanent_address': 'Neuer Jungfernstieg 21, 20354 Hamburg, Germany',
            'arrival_date': now - timedelta(days=1),
            'departure_date': now + timedelta(days=5),
            'purpose_of_stay': 'business',
            'authority_name': 'Bheemili Marine Police Station (Visakhapatnam City Police)',
            'police_station_jurisdiction': 'Rushikonda - Bheemili Beach Beat Zone',
            'submission_mode': 'online',
            'submission_ref': 'ACK-BHM-POLICE-2026-881',
            'state': 'submitted',
            'is_paperless': True,
            'verification_status': 'verified',
        }
        if not gr:
            GuestReport.create(gr_vals)
        else:
            gr.write(gr_vals)

        # Routine Police Visit by Bheemili Sub-Inspector
        duty_user = users_map.get('Surya Prakash Rao') or env.user
        pv = PoliceVisit.search([('officer_name', 'ilike', 'Satyanarayana')], limit=1)
        pv_vals = {
            'police_station': 'Bheemili Law & Order Police Station',
            'officer_name': 'K. Satyanarayana',
            'officer_rank': 'psi',
            'officer_badge_no': 'AP-VIZAG-SI-4412',
            'visit_datetime': datetime.combine(today, datetime.strptime("10:30:00", "%H:%M:%S").time()),
            'purpose': 'routine_patrol',
            'met_with_id': duty_user.id,
            'property_id': rb_resort.id,
            'observations': 'Routine Coastal Security Beat verification. Foreign guest register and security gate logs inspected. All registers found in high compliance order. Official station visit diary signed by SI Satyanarayana and Chief Security Officer Surya Prakash Rao.',
            'state': 'completed',
            'follow_up_required': False,
        }
        if not pv:
            PoliceVisit.create(pv_vals)
        else:
            pv.write(pv_vals)

        # Gate Security Logs (EV Vehicle + Paperless Green Pass)
        sec_logs_data = [
            {
                'log_type': 'vehicle',
                'property_id': rb_resort.id,
                'visitor_name': 'Gokaraju Venkata Rama Raju',
                'visitor_phone': '+91 98490 88888',
                'vehicle_number': 'AP 39 TK 9999',
                'vehicle_type': 'car',
                'visiting_guest_id': demo_guests['Gokaraju Venkata Rama Raju'].id,
                'room_id': r_v01.id,
                'eco_transport_type': 'ev',
                'allocated_ev_charging': True,
                'parking_slot': 'EV Bay 01 (Fast DC Charger)',
                'is_paperless_gate_pass': True,
                'entry_datetime': datetime.combine(today, datetime.strptime("11:15:00", "%H:%M:%S").time()),
                'state': 'active',
                'observations': 'Audi e-tron Electric SUV. Allocated to resort fast DC charging station. Digital paperless e-gate pass issued to guest mobile.',
            },
            {
                'log_type': 'vehicle',
                'property_id': rb_resort.id,
                'visitor_name': 'Koganti Tarun Chowdary',
                'visitor_phone': '+91 99890 66666',
                'vehicle_number': 'AP 31 BV 1008',
                'vehicle_type': 'car',
                'visiting_guest_id': demo_guests['Koganti Tarun Chowdary'].id,
                'room_id': r201.id,
                'eco_transport_type': 'standard',
                'parking_slot': 'Executive Suite Bay 201',
                'is_paperless_gate_pass': True,
                'entry_datetime': datetime.combine(today - timedelta(days=3), datetime.strptime("14:30:00", "%H:%M:%S").time()),
                'state': 'active',
                'observations': 'Mercedes E-Class. Chauffeur escorted to driver lounge.',
            },
        ]

        for s_log in sec_logs_data:
            exist_log = SecurityLog.search([('vehicle_number', '=', s_log['vehicle_number'])], limit=1)
            if not exist_log:
                SecurityLog.create(s_log)
            else:
                exist_log.write(s_log)

        print("-> Resort Compliance & Security logs initialized!")

        cr.commit()
        print("=" * 70)
        print("SUCCESS! ALL COASTAL ANDHRA PRADESH DEMO DATA COMMITTED TO DATABASE!")
        print("=" * 70)

if __name__ == '__main__':
    populate_ap_demo_data()
