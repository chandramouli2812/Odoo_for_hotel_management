# -*- coding: utf-8 -*-
"""
Mouli Hotels - Production-Grade Realistic Demo Data Generator
Direct backend loader using Odoo ORM.
"""

from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

def populate_hotel_demo_data(env):
    print("=" * 60)
    print("Starting Mouli Hotels Demo Data Population...")
    print("=" * 60)

    Company = env['res.company']
    company = env.company or Company.search([], limit=1)
    Property = env['hotel.property']
    Building = env['hotel.building']
    Floor = env['hotel.floor']
    Amenity = env['hotel.amenity']
    RoomType = env['hotel.room.type']
    Room = env['hotel.room']
    Partner = env['res.partner']
    Reservation = env['hotel.reservation']
    Folio = env['hotel.folio']
    FolioLine = env['hotel.folio.line']
    FolioPayment = env['hotel.folio.payment']
    Housekeeping = env['hotel.housekeeping.task']

    # 1. AMENITIES
    amenity_specs = [
        ('WIFI', 'High-Speed Wi-Fi 6', 'Ultra-fast 1 Gbps wireless internet in all rooms and common areas'),
        ('KING_BED', 'King Size Plush Bed', 'Hypoallergenic luxury king mattress with 400 thread-count Egyptian cotton linens'),
        ('SMART_TV', '55-inch 4K Smart TV', 'Pre-loaded with Netflix, Prime Video, Disney+, and Apple AirPlay'),
        ('BALCONY', 'Private Ocean View Balcony', 'Panoramic sea view terrace with loungers and dining table'),
        ('JACUZZI', 'Private Jacuzzi / Whirlpool Tub', 'Heated hydromassage spa tub with aromatherapy bath salts'),
        ('MINIBAR', 'Artisan Mini Bar & Nespresso', 'Stocked gourmet snacks, premium spirits, craft beer, and Nespresso capsule machine'),
        ('CLIMATE', 'Silent Climate Control AC', 'Individual digital inverter climate thermostat with air purifier'),
        ('SAFE', 'Digital In-Room Safe', 'Laptop-sized electronic biometric and digital code security safe'),
        ('DESK', 'Ergonomic Executive Desk', 'Solid wood workstation with ergonomic Herman Miller chair and USB-C docks'),
        ('BUTLER', '24/7 Dedicated Butler Service', 'Round-the-clock personal concierge and butler assistance on demand'),
        ('BREAKFAST', 'Complimentary Gourmet Breakfast', 'Daily international buffet breakfast or in-room breakfast tray'),
    ]
    amenities = {}
    for code, name, desc in amenity_specs:
        amenity = Amenity.search([('code', '=', code)], limit=1)
        if not amenity:
            amenity = Amenity.create({'code': code, 'name': name, 'description': desc})
        amenities[code] = amenity
    print(f"-> Amenities loaded: {len(amenities)}")

    # 2. PROPERTIES
    prop_specs = [
        {
            'code': 'GHLR',
            'name': 'Grand Horizon Luxury Resort & Spa',
            'street': '77 Ocean Drive',
            'city': 'Miami Beach',
            'phone': '+1 305-555-0199',
            'email': 'reservations@grandhorizonresort.com',
            'website': 'https://www.grandhorizonresort.com',
        },
        {
            'code': 'RPHS',
            'name': 'The Royal Palms Hotel & Suites',
            'street': '10 Kensington High Street',
            'city': 'London',
            'phone': '+44 20 7946 0912',
            'email': 'stay@royalpalmshotel.com',
            'website': 'https://www.royalpalmshotel.com',
        },
        {
            'code': 'MMHR',
            'name': 'Mouli Mountain Heritage Retreat',
            'street': 'Valley View Road',
            'city': 'Manali',
            'phone': '+91 80 4123 4567',
            'email': 'concierge@mouliretreat.com',
            'website': 'https://www.mouliretreat.com',
        },
    ]
    properties = {}
    for p_spec in prop_specs:
        prop = Property.search([('code', '=', p_spec['code'])], limit=1)
        if not prop:
            prop = Property.create(p_spec)
        else:
            prop.write(p_spec)
        properties[p_spec['code']] = prop
    print(f"-> Properties loaded: {len(properties)}")

    # 3. BUILDINGS & FLOORS
    ghlr = properties['GHLR']
    b_ocean = Building.search([('property_id', '=', ghlr.id), ('name', '=', 'Main Ocean Tower')], limit=1)
    if not b_ocean:
        b_ocean = Building.create({'name': 'Main Ocean Tower', 'code': 'MOT', 'property_id': ghlr.id, 'floor_count': 3})
    
    b_villas = Building.search([('property_id', '=', ghlr.id), ('name', '=', 'Beachfront Villas')], limit=1)
    if not b_villas:
        b_villas = Building.create({'name': 'Beachfront Villas', 'code': 'BFV', 'property_id': ghlr.id, 'floor_count': 1})

    b_penthouse = Building.search([('property_id', '=', ghlr.id), ('name', '=', 'Royal Sky Penthouse')], limit=1)
    if not b_penthouse:
        b_penthouse = Building.create({'name': 'Royal Sky Penthouse', 'code': 'RSP', 'property_id': ghlr.id, 'floor_count': 1})

    floors = {}
    floor_specs = [
        ('Ground Floor', 0, b_ocean.id),
        ('Floor 1', 1, b_ocean.id),
        ('Floor 2', 2, b_ocean.id),
        ('Floor 3', 3, b_ocean.id),
        ('Villa Pavilion', 0, b_villas.id),
        ('Penthouse Sky Deck', 4, b_penthouse.id),
    ]
    for fl_name, fl_num, b_id in floor_specs:
        fl = Floor.search([('property_id', '=', ghlr.id), ('name', '=', fl_name)], limit=1)
        if not fl:
            fl = Floor.create({'name': fl_name, 'floor_number': fl_num, 'property_id': ghlr.id, 'building_id': b_id})
        floors[fl_name] = fl
    print(f"-> Buildings and floors initialized for {ghlr.name}")

    # 4. ROOM TYPES
    type_specs = [
        {
            'code': 'DLX_K',
            'name': 'Deluxe King Room',
            'capacity': 3,
            'adult_capacity': 2,
            'child_capacity': 1,
            'list_price': 3500.0,
            'description': '<p>Spacious 42 sqm room featuring a plush king bed, marble en-suite bathroom, rain shower, and private balcony.</p>',
            'amenities': ['WIFI', 'KING_BED', 'SMART_TV', 'BALCONY', 'CLIMATE', 'SAFE', 'BREAKFAST']
        },
        {
            'code': 'EXEC_S',
            'name': 'Executive Business Suite',
            'capacity': 4,
            'adult_capacity': 3,
            'child_capacity': 1,
            'list_price': 6500.0,
            'description': '<p>Expansive 65 sqm suite with separate living parlor, ergonomic workstation, walk-in closet, and executive lounge access.</p>',
            'amenities': ['WIFI', 'KING_BED', 'SMART_TV', 'BALCONY', 'MINIBAR', 'CLIMATE', 'SAFE', 'DESK', 'BREAKFAST']
        },
        {
            'code': 'OCN_V',
            'name': 'Oceanfront Luxury Villa',
            'capacity': 5,
            'adult_capacity': 4,
            'child_capacity': 2,
            'list_price': 12000.0,
            'description': '<p>Stand-alone 120 sqm private villa directly overlooking the ocean, featuring private plunge pool and sun terrace.</p>',
            'amenities': ['WIFI', 'KING_BED', 'SMART_TV', 'BALCONY', 'JACUZZI', 'MINIBAR', 'CLIMATE', 'SAFE', 'BUTLER', 'BREAKFAST']
        },
        {
            'code': 'PRES_P',
            'name': 'Presidential Penthouse Suite',
            'capacity': 8,
            'adult_capacity': 6,
            'child_capacity': 2,
            'list_price': 25000.0,
            'description': '<p>The pinnacle of luxury at 250 sqm. Features 3 en-suite bedrooms, private rooftop jacuzzi, dining salon for 8, and 24/7 butler.</p>',
            'amenities': ['WIFI', 'KING_BED', 'SMART_TV', 'BALCONY', 'JACUZZI', 'MINIBAR', 'CLIMATE', 'SAFE', 'DESK', 'BUTLER', 'BREAKFAST']
        },
        {
            'code': 'STD_T',
            'name': 'Standard Comfort Twin Room',
            'capacity': 2,
            'adult_capacity': 2,
            'child_capacity': 0,
            'list_price': 2200.0,
            'description': '<p>Contemporary 30 sqm room designed with two twin beds, premium acoustic insulation, work corner, and rainfall shower.</p>',
            'amenities': ['WIFI', 'SMART_TV', 'CLIMATE', 'SAFE', 'BREAKFAST']
        },
    ]
    room_types = {}
    for t_spec in type_specs:
        rt = RoomType.search([('code', '=', t_spec['code'])], limit=1)
        amenity_records = [amenities[code].id for code in t_spec['amenities'] if code in amenities]
        vals = {
            'code': t_spec['code'],
            'name': t_spec['name'],
            'capacity': t_spec['capacity'],
            'adult_capacity': t_spec['adult_capacity'],
            'child_capacity': t_spec['child_capacity'],
            'list_price': t_spec['list_price'],
            'description': t_spec['description'],
            'amenity_ids': [(6, 0, amenity_records)],
        }
        if not rt:
            rt = RoomType.create(vals)
        else:
            rt.write(vals)
        room_types[t_spec['code']] = rt
    print(f"-> Room Types loaded: {len(room_types)}")

    # 5. ROOMS
    room_definitions = [
        # (room_number, prop_code, type_code, occ_stat, hk_stat, maint_stat, floor_key, building_obj, notes)
        ('101', 'GHLR', 'DLX_K', 'occupied', 'clean', 'operational', 'Floor 1', b_ocean, 'Ground level with garden access'),
        ('102', 'GHLR', 'DLX_K', 'vacant', 'clean', 'operational', 'Floor 1', b_ocean, 'Corner room, quiet and sunny'),
        ('103', 'GHLR', 'STD_T', 'occupied', 'clean', 'operational', 'Floor 1', b_ocean, 'Standard twin bedding'),
        ('104', 'GHLR', 'STD_T', 'vacant', 'dirty', 'operational', 'Floor 1', b_ocean, 'Guest checked out 2 hours ago, cleaning queued'),
        ('105', 'GHLR', 'DLX_K', 'vacant', 'inspected', 'operational', 'Floor 1', b_ocean, 'Inspected & ready for high-profile check-in'),
        ('201', 'GHLR', 'EXEC_S', 'occupied', 'clean', 'operational', 'Floor 2', b_ocean, 'Executive business traveler in-house'),
        ('202', 'GHLR', 'EXEC_S', 'vacant', 'clean', 'operational', 'Floor 2', b_ocean, 'Panoramic ocean view suite'),
        ('203', 'GHLR', 'DLX_K', 'reserved', 'clean', 'operational', 'Floor 2', b_ocean, 'Reserved for confirmed arrival'),
        ('204', 'GHLR', 'DLX_K', 'vacant', 'cleaning', 'operational', 'Floor 2', b_ocean, 'Housekeeping attendant on duty'),
        ('205', 'GHLR', 'STD_T', 'vacant', 'clean', 'operational', 'Floor 2', b_ocean, 'Courtyard garden view'),
        ('301', 'GHLR', 'EXEC_S', 'vacant', 'clean', 'operational', 'Floor 3', b_ocean, 'Top floor executive suite'),
        ('302', 'GHLR', 'DLX_K', 'vacant', 'dirty', 'maintenance', 'Floor 3', b_ocean, 'Scheduled AC condenser maintenance'),
        ('303', 'GHLR', 'DLX_K', 'occupied', 'clean', 'operational', 'Floor 3', b_ocean, 'Long-term guest in residence'),
        ('V01', 'GHLR', 'OCN_V', 'occupied', 'clean', 'operational', 'Villa Pavilion', b_villas, 'Private infinity pool villa with butler'),
        ('V02', 'GHLR', 'OCN_V', 'vacant', 'inspected', 'operational', 'Villa Pavilion', b_villas, 'Fully inspected luxury villa'),
        ('V03', 'GHLR', 'OCN_V', 'reserved', 'clean', 'operational', 'Villa Pavilion', b_villas, 'Upcoming VIP honeymoon stay'),
        ('P01', 'GHLR', 'PRES_P', 'occupied', 'clean', 'operational', 'Penthouse Sky Deck', b_penthouse, 'Grand Penthouse in residence'),
        ('P02', 'GHLR', 'PRES_P', 'vacant', 'inspected', 'operational', 'Penthouse Sky Deck', b_penthouse, 'Penthouse ready for dignitary arrival'),
    ]

    rooms = {}
    for r_num, p_code, t_code, occ, hk, maint, fl_key, b_obj, notes in room_definitions:
        prop = properties[p_code]
        rm_type = room_types[t_code]
        fl_obj = floors.get(fl_key)
        
        room = Room.search([('room_number', '=', r_num), ('property_id', '=', prop.id)], limit=1)
        vals = {
            'room_number': r_num,
            'property_id': prop.id,
            'room_type_id': rm_type.id,
            'building_id': b_obj.id if b_obj else False,
            'floor_id': fl_obj.id if fl_obj else False,
            'occupancy_status': occ,
            'housekeeping_status': hk,
            'maintenance_status': maint,
            'notes': notes,
        }
        if not room:
            room = Room.create(vals)
        else:
            room.write(vals)
        rooms[(p_code, r_num)] = room
    print(f"-> Physical Rooms loaded: {len(rooms)}")

    # 6. GUESTS
    guest_specs = [
        {
            'name': 'Marcus Aurelius Tan',
            'email': 'marcus.tan@singaporefin.sg',
            'phone': '+65 9123 4567',
            'is_hotel_guest': True,
            'id_type': 'passport',
            'id_number': 'SG99018234E',
            'vip_status': 'platinum',
            'gender': 'male',
            'guest_notes': 'Presidential Penthouse regular guest, prefers private butler check-in and fresh orchids.',
        },
        {
            'name': 'Alexander Wright',
            'email': 'alex.wright@techventures.io',
            'phone': '+1 415-555-8921',
            'is_hotel_guest': True,
            'id_type': 'passport',
            'id_number': 'US982314562',
            'vip_status': 'platinum',
            'gender': 'male',
            'guest_notes': 'High floor preference, sparkling San Pellegrino water, daily dry cleaning before 9 AM.',
        },
        {
            'name': 'Priya Sharma',
            'email': 'priya.sharma@consultingcorp.in',
            'phone': '+91 98200 45678',
            'is_hotel_guest': True,
            'id_type': 'national_id',
            'id_number': '9823-4512-8871',
            'vip_status': 'gold',
            'gender': 'female',
            'guest_notes': 'Strict vegetarian breakfast buffet, extra hypoallergenic pillows requested.',
        },
        {
            'name': 'Liam O\'Connor',
            'email': 'liam.oconnor@dublintech.ie',
            'phone': '+353 87 123 4567',
            'is_hotel_guest': True,
            'id_type': 'passport',
            'id_number': 'IE882910345',
            'vip_status': 'silver',
            'gender': 'male',
            'guest_notes': 'Honeymoon vacation stay. Requested Veuve Clicquot champagne on arrival.',
        },
        {
            'name': 'Elena Rostova',
            'email': 'elena.rostova@designstudio.fr',
            'phone': '+33 6 12 34 56 78',
            'is_hotel_guest': True,
            'id_type': 'passport',
            'id_number': 'FR667823412',
            'vip_status': 'gold',
            'gender': 'female',
            'guest_notes': 'Allergic to feather duvets. Booked private aromatherapy spa session.',
        },
        {
            'name': 'David Miller',
            'email': 'david.miller@globalshipping.co.uk',
            'phone': '+44 7700 900123',
            'is_hotel_guest': True,
            'id_type': 'passport',
            'id_number': 'GB441209341',
            'vip_status': 'silver',
            'gender': 'male',
            'guest_notes': 'Airport chauffeur transfer required at 06:00 AM.',
        },
        {
            'name': 'Ananya Iyer',
            'email': 'ananya.iyer@healthsciences.org',
            'phone': '+91 99401 23456',
            'is_hotel_guest': True,
            'id_type': 'driving_license',
            'id_number': 'DL-0420110023',
            'vip_status': 'standard',
            'gender': 'female',
            'guest_notes': 'Family holiday trip. Baby crib required in room.',
        },
        {
            'name': 'Carlos Rodriguez',
            'email': 'carlos.rodriguez@madridtrade.es',
            'phone': '+34 600 123 456',
            'is_hotel_guest': True,
            'id_type': 'national_id',
            'id_number': '48291034-K',
            'vip_status': 'standard',
            'gender': 'male',
            'guest_notes': 'Completed stay, express checkout used.',
        },
    ]

    guests = {}
    for g_spec in guest_specs:
        p = Partner.search([('email', '=', g_spec['email'])], limit=1)
        if not p:
            p = Partner.create(g_spec)
        else:
            p.write(g_spec)
        guests[g_spec['name']] = p
    print(f"-> Hotel Guests loaded: {len(guests)}")

    # 7. RESERVATIONS, ACTIVE STAYS & FOLIOS
    now = datetime.now()
    
    stay_definitions = [
        # (guest_name, prop_code, room_num, type_code, offset_in, nights, adults, children, rate, adv_amt, adv_method, status, extra_lines, extra_payments)
        {
            'guest': 'Marcus Aurelius Tan',
            'prop': 'GHLR',
            'room': 'P01',
            'type': 'PRES_P',
            'in_offset': -2,
            'nights': 5,
            'adults': 2,
            'children': 0,
            'rate': 25000.0,
            'adv_amt': 50000.0,
            'adv_method': 'card',
            'status': 'check_in',
            'extra_lines': [
                ('Presidential Caviar & Champagne In-Room Dinner', 'restaurant', 1, 14500.0),
                ('Signature 90-min Balinese Couples Spa Treatment', 'spa', 2, 8500.0),
                ('Premium Vintage Wine & Cognac Minibar Restock', 'minibar', 1, 6200.0),
            ],
            'extra_payments': [
                ('Mid-Stay Credit Card Payment', 30000.0, 'card', 'AUTH-VISA-98214')
            ]
        },
        {
            'guest': 'Alexander Wright',
            'prop': 'GHLR',
            'room': '201',
            'type': 'EXEC_S',
            'in_offset': -1,
            'nights': 4,
            'adults': 1,
            'children': 0,
            'rate': 6500.0,
            'adv_amt': 6500.0,
            'adv_method': 'card',
            'status': 'check_in',
            'extra_lines': [
                ('Executive Business Club Lunch', 'restaurant', 2, 1850.0),
                ('Express Dry Cleaning & Suit Pressing', 'laundry', 1, 1200.0),
            ],
            'extra_payments': []
        },
        {
            'guest': 'Priya Sharma',
            'prop': 'GHLR',
            'room': '101',
            'type': 'DLX_K',
            'in_offset': -3,
            'nights': 4,
            'adults': 2,
            'children': 1,
            'rate': 3500.0,
            'adv_amt': 3500.0,
            'adv_method': 'upi',
            'status': 'check_in',
            'extra_lines': [
                ('Organic Vegetarian Gourmet Dinner (3 Pax)', 'restaurant', 1, 2400.0),
                ('Artisan Herbal Tea & Snack Platter', 'restaurant', 2, 650.0),
            ],
            'extra_payments': [
                ('UPI Payment via Front-Desk QR', 5000.0, 'upi', 'UPI-REF-894723')
            ]
        },
        {
            'guest': 'Liam O\'Connor',
            'prop': 'GHLR',
            'room': 'V01',
            'type': 'OCN_V',
            'in_offset': -1,
            'nights': 6,
            'adults': 2,
            'children': 0,
            'rate': 12000.0,
            'adv_amt': 24000.0,
            'adv_method': 'card',
            'status': 'check_in',
            'extra_lines': [
                ('Beachside Candlelight 5-Course Honeymoon Dinner', 'restaurant', 1, 9500.0),
                ('Private Sunset Yacht Charter Experience', 'other', 1, 18000.0),
            ],
            'extra_payments': []
        },
        {
            'guest': 'Elena Rostova',
            'prop': 'GHLR',
            'room': '303',
            'type': 'DLX_K',
            'in_offset': -2,
            'nights': 3,
            'adults': 1,
            'children': 0,
            'rate': 3500.0,
            'adv_amt': 3500.0,
            'adv_method': 'card',
            'status': 'check_in',
            'extra_lines': [
                ('Hydrotherapy Mineral Bath & Swedish Massage', 'spa', 1, 4800.0),
            ],
            'extra_payments': [
                ('Front Desk Cash Deposit', 3500.0, 'cash', 'RECEIPT-09823')
            ]
        },
        {
            'guest': 'David Miller',
            'prop': 'GHLR',
            'room': '203',
            'type': 'DLX_K',
            'in_offset': 1,
            'nights': 3,
            'adults': 1,
            'children': 0,
            'rate': 3500.0,
            'adv_amt': 3500.0,
            'adv_method': 'bank',
            'status': 'confirmed',
            'extra_lines': [],
            'extra_payments': []
        },
        {
            'guest': 'Ananya Iyer',
            'prop': 'GHLR',
            'room': 'V03',
            'type': 'OCN_V',
            'in_offset': 2,
            'nights': 4,
            'adults': 4,
            'children': 2,
            'rate': 12000.0,
            'adv_amt': 12000.0,
            'adv_method': 'upi',
            'status': 'confirmed',
            'extra_lines': [],
            'extra_payments': []
        },
        {
            'guest': 'Carlos Rodriguez',
            'prop': 'GHLR',
            'room': '103',
            'type': 'STD_T',
            'in_offset': -4,
            'nights': 3,
            'adults': 1,
            'children': 0,
            'rate': 2200.0,
            'adv_amt': 2200.0,
            'adv_method': 'cash',
            'status': 'check_out',
            'extra_lines': [
                ('Airport Shuttle Express Drop', 'other', 1, 1500.0)
            ],
            'extra_payments': [
                ('Checkout Balance Final Settlement (Cash)', 5900.0, 'cash', 'CASH-REC-4412')
            ]
        },
    ]

    for s_def in stay_definitions:
        g = guests[s_def['guest']]
        p = properties[s_def['prop']]
        rt = room_types[s_def['type']]
        rm = rooms[(s_def['prop'], s_def['room'])]
        
        ci = now + timedelta(days=s_def['in_offset'])
        co = ci + timedelta(days=s_def['nights'])

        # Check if already created
        existing_res = Reservation.search([
            ('guest_id', '=', g.id),
            ('room_id', '=', rm.id),
            ('state', '=', s_def['status']),
        ], limit=1)

        if not existing_res:
            res_vals = {
                'guest_id': g.id,
                'property_id': p.id,
                'room_type_id': rt.id,
                'room_id': rm.id,
                'check_in': ci,
                'check_out': co,
                'adults': s_def['adults'],
                'children': s_def['children'],
                'rate_per_night': s_def['rate'],
                'advance_payment': s_def['adv_amt'],
                'advance_payment_method': s_def['adv_method'],
                'advance_payment_ref': f"ADV-{s_def['adv_method'].upper()}-001",
                'state': s_def['status'],
                'booking_source': 'direct',
            }
            res = Reservation.create(res_vals)
            
            # Setup Folio
            folio = Folio.create({
                'reservation_id': res.id,
                'guest_id': g.id,
                'room_id': rm.id,
                'property_id': p.id,
                'date_order': ci,
            })
            res.folio_id = folio.id

            # Room stay charge line
            FolioLine.create({
                'folio_id': folio.id,
                'name': f"Room Stay: {rm.name} ({s_def['nights']} Nights)",
                'service_type': 'room',
                'quantity': s_def['nights'],
                'price_unit': s_def['rate'],
            })

            # Advance payment record
            if s_def['adv_amt'] > 0:
                FolioPayment.create({
                    'folio_id': folio.id,
                    'name': f"Advance Deposit for {res.name}",
                    'amount': s_def['adv_amt'],
                    'payment_method': s_def['adv_method'],
                    'reference': f"ADV-DEP-{s_def['adv_method'].upper()}",
                    'is_advance': True,
                    'payment_date': ci,
                })

            # Extra service charge lines (F&B, Spa, Minibar, Laundry)
            for line_name, stype, qty, price in s_def['extra_lines']:
                FolioLine.create({
                    'folio_id': folio.id,
                    'name': line_name,
                    'service_type': stype,
                    'quantity': qty,
                    'price_unit': price,
                })

            # Extra payments
            for p_name, p_amt, p_method, p_ref in s_def['extra_payments']:
                FolioPayment.create({
                    'folio_id': folio.id,
                    'name': p_name,
                    'amount': p_amt,
                    'payment_method': p_method,
                    'reference': p_ref,
                    'payment_date': now,
                })

            # Link room state
            if s_def['status'] == 'check_in':
                rm.write({
                    'occupancy_status': 'occupied',
                    'current_reservation_id': res.id,
                    'housekeeping_status': 'clean',
                })
            elif s_def['status'] == 'confirmed':
                rm.write({
                    'occupancy_status': 'reserved',
                })
            elif s_def['status'] == 'check_out':
                rm.write({
                    'occupancy_status': 'vacant',
                    'housekeeping_status': 'clean',
                })

    print("-> Reservations, Folios, Stay Charges & Payments initialized successfully!")

    # 8. HOUSEKEEPING WORK ORDERS
    hk_tasks_spec = [
        (rooms[('GHLR', '104')], 'checkout_clean', 'in_progress', '3', 'Urgent checkout turnaround required for VIP arrival'),
        (rooms[('GHLR', '204')], 'stayover_clean', 'in_progress', '1', 'Daily linen change and bathroom restocking'),
        (rooms[('GHLR', '302')], 'deep_clean', 'draft', '2', 'Complete ozone sanitization & carpet steam clean post AC repair'),
        (rooms[('GHLR', '105')], 'inspection', 'done', '2', 'Executive supervisor inspection passed with 100% score'),
    ]
    for r_obj, t_type, t_state, priority, notes in hk_tasks_spec:
        task = Housekeeping.search([('room_id', '=', r_obj.id), ('task_type', '=', t_type)], limit=1)
        if not task:
            Housekeeping.create({
                'room_id': r_obj.id,
                'task_type': t_type,
                'state': t_state,
                'priority': priority,
                'notes': notes,
                'scheduled_date': now.date(),
            })
    print("-> Housekeeping tasks initialized!")

    print("=" * 60)
    print("Mouli Hotels Demo Data Imported Successfully!")
    print("=" * 60)
