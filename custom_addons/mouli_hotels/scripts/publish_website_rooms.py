# -*- coding: utf-8 -*-
"""
Publishes luxury room types on the website, sets high-resolution photography,
configures website highlights/ribbons, and populates sample web booking leads.
"""

import sys
import os
import base64
from datetime import datetime, timedelta

sys.path.insert(0, r'D:\Odoo_sample\server')
import odoo
from odoo.tools import config
config.parse_config(['-c', r'D:\Odoo_sample\server\odoo.conf'])
from odoo.modules.registry import Registry

def publish_rooms_and_setup_leads():
    registry = Registry('Odoo_sample')
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        now = datetime.now()
        today = now.date()

        print("=" * 70)
        print("PUBLISHING ROOMS ON WEBSITE & INITIALIZING LEAD GENERATION")
        print("=" * 70)

        # 1. Image Assets Path
        img_dir = r'd:\Odoo_sample\server\custom_addons\mouli_hotels\static\src\img'
        
        def load_b64(filename):
            fp = os.path.join(img_dir, filename)
            if os.path.exists(fp):
                with open(fp, 'rb') as f:
                    return base64.b64encode(f.read()).decode('ascii')
            return False

        img_villa = load_b64('villa_luxury_oceanfront.jpg')
        img_penthouse = load_b64('penthouse_presidential_suite.jpg')
        img_suite = load_b64('suite_executive_business.jpg')
        img_deluxe = load_b64('room_deluxe_king.jpg')

        # 2. Target Property: RB Resorts
        Property = env['hotel.property']
        rb_resort = Property.search([('name', 'ilike', 'RB Resorts')], limit=1)

        # 3. Configure Room Types
        RoomType = env['hotel.room.type']

        room_type_configs = [
            {
                'name_match': 'Villa',
                'vals': {
                    'name': 'Oceanfront Luxury Villa',
                    'code': 'OCN_V',
                    'list_price': 18000.0,
                    'capacity': 5,
                    'adult_capacity': 4,
                    'child_capacity': 2,
                    'is_published': True,
                    'website_ribbon': 'luxury',
                    'website_sequence': 1,
                    'website_short_description': 'Private Sunrise Plunge Pool Villa with direct Rushikonda beach access and personal sundeck.',
                    'website_features': 'Private Infinity Plunge Pool • Oceanfront Sun Deck • Master King Bed • Complimentary Andhra Breakfast • Dedicated 24/7 Butler • Private Dining Gazebo',
                    'description': '<p>Escape to our crown jewel oceanfront villa perched directly along the Rushikonda coast. Features an exclusive infinity plunge pool, sprawling teakwood sun deck, master king bedroom with panoramic glass doors, and bespoke Coastal Andhra hospitality.</p>',
                    'image_1920': img_villa,
                }
            },
            {
                'name_match': 'Penthouse',
                'vals': {
                    'name': 'Presidential Penthouse Suite',
                    'code': 'PRES_P',
                    'list_price': 25000.0,
                    'capacity': 8,
                    'adult_capacity': 6,
                    'child_capacity': 2,
                    'is_published': True,
                    'website_ribbon': 'luxury',
                    'website_sequence': 2,
                    'website_short_description': 'Panoramic 180° Bheemili Marine Drive view with private heated terrace jacuzzi and luxury lounge.',
                    'website_features': 'Private Balcony Jacuzzi • Floor-to-Ceiling Sea View • Grand King Suite • Coastal Seafood Dining • Presidential In-Room Bar & Nespresso • High-Speed Wi-Fi',
                    'description': '<p>The pinnacle of coastal opulence. Our top-floor Presidential Penthouse offers unobstructed vistas of the Bay of Bengal, a heated outdoor jacuzzi on the private terrace, a lavish living salon, and round-the-clock personalized butler service.</p>',
                    'image_1920': img_penthouse,
                }
            },
            {
                'name_match': 'Suite',
                'vals': {
                    'name': 'Executive Business Suite',
                    'code': 'EXEC_S',
                    'list_price': 6500.0,
                    'capacity': 4,
                    'adult_capacity': 3,
                    'child_capacity': 1,
                    'is_published': True,
                    'website_ribbon': 'popular',
                    'website_sequence': 3,
                    'website_short_description': 'Executive work lounge, private sea-facing balcony, and high-speed satellite Wi-Fi for port & business leaders.',
                    'website_features': 'Private Ocean Balcony • Ergonomic Mahogany Workstation • High-Speed 500 Mbps Wi-Fi • Express Suit Steaming • Executive Boardroom Access • King Bed',
                    'description': '<p>Tailored for discerning business executives and corporate travelers. Features a distinct living area, dedicated ergonomic workspace, private balcony with sea breeze, and complimentary business lounge privileges.</p>',
                    'image_1920': img_suite,
                }
            },
            {
                'name_match': 'Deluxe',
                'vals': {
                    'name': 'Deluxe King Room',
                    'code': 'DLX_K',
                    'list_price': 4500.0,
                    'capacity': 3,
                    'adult_capacity': 2,
                    'child_capacity': 1,
                    'is_published': True,
                    'website_ribbon': 'featured',
                    'website_sequence': 4,
                    'website_short_description': 'Spacious coastal king retreat overlooking tropical coconut gardens and refreshing ocean breezes.',
                    'website_features': 'Lush Garden & Sea Breeze Balcony • King Size Bed • Organic Herbal Toiletries • Andhra Buffet Breakfast • Swimming Pool Access',
                    'description': '<p>A serene haven blending contemporary comfort with traditional Andhra aesthetics. Featuring plush king bedding, garden view sit-out balcony, and full access to resort amenities and swimming pools.</p>',
                    'image_1920': img_deluxe,
                }
            },
            {
                'name_match': 'Standard',
                'vals': {
                    'name': 'Standard Comfort Twin Room',
                    'code': 'STD_T',
                    'list_price': 2800.0,
                    'capacity': 2,
                    'adult_capacity': 2,
                    'child_capacity': 0,
                    'is_published': True,
                    'website_ribbon': 'deal',
                    'website_sequence': 5,
                    'website_short_description': 'Cozy twin beds with resort pool access, perfect for weekend getaways and touring companions.',
                    'website_features': 'Twin Beds • Pool View • High-Speed Wi-Fi • En-Suite Rain Shower • Complimentary Buffet Breakfast',
                    'description': '<p>Smart, comfortable, and functional accommodations equipped with twin beds, modern en-suite amenities, and high-speed internet.</p>',
                    'image_1920': img_deluxe,
                }
            },
        ]

        for cfg in room_type_configs:
            rt = RoomType.search([('name', 'ilike', cfg['name_match'])], limit=1)
            if rt:
                rt.write(cfg['vals'])
                print(f"-> Published Room Type: {rt.name} (Rs.{rt.list_price:,.0f}/nt) - Ribbon: {rt.website_ribbon}")
            else:
                rt = RoomType.create(cfg['vals'])
                print(f"-> Created & Published: {rt.name}")

        # 4. Ensure Website Header Navigation Menu
        Website = env['website']
        Menu = env['website.menu']
        main_website = Website.search([], limit=1)
        if main_website and main_website.menu_id:
            existing_menu = Menu.search([
                ('website_id', '=', main_website.id),
                ('url', '=', '/rooms')
            ], limit=1)
            if not existing_menu:
                Menu.create({
                    'name': 'Rooms & Suites',
                    'url': '/rooms',
                    'parent_id': main_website.menu_id.id,
                    'website_id': main_website.id,
                    'sequence': 20,
                })
                print("-> Website Header Menu 'Rooms & Suites' created successfully!")
            else:
                existing_menu.write({'sequence': 20, 'name': 'Rooms & Suites'})
                print("-> Website Header Menu 'Rooms & Suites' verified!")

        # 5. Populate Sample Website Booking Leads for Client Demo
        Partner = env['res.partner']
        Lead = env['crm.lead']
        Reservation = env['hotel.reservation']
        Tag = env['crm.tag']

        web_tag = Tag.search([('name', '=', 'Website Room Lead')], limit=1)
        if not web_tag:
            web_tag = Tag.create({'name': 'Website Room Lead', 'color': 4})

        villa_rt = RoomType.search([('name', 'ilike', 'Villa')], limit=1)
        suite_rt = RoomType.search([('name', 'ilike', 'Suite')], limit=1)

        # Sample Web Lead 1: Vijayawada Businessman inquiring for Oceanfront Villa
        p1 = Partner.search([('email', '=', 'ramesh.ch@vijayawadabuilders.in')], limit=1)
        if not p1:
            p1 = Partner.create({
                'name': 'Ramesh Chowdary',
                'email': 'ramesh.ch@vijayawadabuilders.in',
                'phone': '+91 98480 33333',
                'city': 'Vijayawada',
                'is_hotel_guest': True,
                'vip_status': 'gold',
            })

        l1 = Lead.search([('partner_id', '=', p1.id)], limit=1)
        if not l1:
            l1 = Lead.create({
                'name': f"Website Inquiry: Oceanfront Villa - Ramesh Chowdary",
                'partner_id': p1.id,
                'contact_name': p1.name,
                'phone': p1.phone,
                'email_from': p1.email,
                'city': p1.city,
                'expected_revenue': 54000.0, # 3 nights * 18k
                'type': 'opportunity',
                'priority': '3',
                'tag_ids': [(4, web_tag.id)],
                'description': """--- RESORT WEBSITE ROOM INQUIRY ---
Room Type: Oceanfront Luxury Villa
Property: RB Luxury Beach Resort & Spa
Dates: Tomorrow to +3 Days (3 Nights)
Guests: 2 Adults, 1 Child
Meal Plan: CP - Bed & Breakfast (Complimentary)
Estimated Revenue: ₹54,000.00
Special Requests: Beach villa sunrise view, poornam boorelu welcome drink, baby crib.
Submitted online via /rooms web portal.""",
            })

            # Create Draft Reservation linked to CRM Lead
            Reservation.create({
                'guest_id': p1.id,
                'property_id': rb_resort.id if rb_resort else False,
                'room_type_id': villa_rt.id,
                'check_in': datetime.combine(today + timedelta(days=2), datetime.strptime("14:00:00", "%H:%M:%S").time()),
                'check_out': datetime.combine(today + timedelta(days=5), datetime.strptime("11:00:00", "%H:%M:%S").time()),
                'adults': 2,
                'children': 1,
                'meal_plan': 'cp',
                'rate_per_night': 18000.0,
                'state': 'draft',
                'booking_source': 'website',
                'crm_lead_id': l1.id,
                'dietary_notes': 'Strict vegetarian breakfast.',
                'notes': f"Direct Website Lead #{l1.id}. Inquired from Vijayawada.",
            })
            print(f"-> Generated Web Lead 1: {l1.name} (Rs.54,000 expected revenue)")

        # Sample Web Lead 2: Hyderabad IT Executive inquiring for Executive Business Suite
        p2 = Partner.search([('email', '=', 'karthik.reddy@hitechhyd.org')], limit=1)
        if not p2:
            p2 = Partner.create({
                'name': 'Karthik Varma',
                'email': 'karthik.reddy@hitechhyd.org',
                'phone': '+91 99890 22222',
                'city': 'Hyderabad',
                'is_hotel_guest': True,
                'vip_status': 'silver',
            })

        l2 = Lead.search([('partner_id', '=', p2.id)], limit=1)
        if not l2:
            l2 = Lead.create({
                'name': f"Website Inquiry: Executive Suite - Karthik Varma",
                'partner_id': p2.id,
                'contact_name': p2.name,
                'phone': p2.phone,
                'email_from': p2.email,
                'city': p2.city,
                'expected_revenue': 19500.0, # 3 nights * 6.5k
                'type': 'opportunity',
                'priority': '2',
                'tag_ids': [(4, web_tag.id)],
                'description': """--- RESORT WEBSITE ROOM INQUIRY ---
Room Type: Executive Business Suite
Property: RB Luxury Beach Resort & Spa
Dates: Next Weekend (3 Nights)
Guests: 2 Adults
Meal Plan: CP - Bed & Breakfast
Estimated Revenue: ₹19,500.00
Special Requests: High-speed Wi-Fi essential, late check-in at 20:00 PM.
Submitted online via /rooms web portal.""",
            })

            Reservation.create({
                'guest_id': p2.id,
                'property_id': rb_resort.id if rb_resort else False,
                'room_type_id': suite_rt.id,
                'check_in': datetime.combine(today + timedelta(days=5), datetime.strptime("14:00:00", "%H:%M:%S").time()),
                'check_out': datetime.combine(today + timedelta(days=8), datetime.strptime("11:00:00", "%H:%M:%S").time()),
                'adults': 2,
                'children': 0,
                'meal_plan': 'cp',
                'rate_per_night': 6500.0,
                'state': 'draft',
                'booking_source': 'website',
                'crm_lead_id': l2.id,
                'notes': f"Direct Website Lead #{l2.id}. Inquired from Hyderabad.",
            })
            print(f"-> Generated Web Lead 2: {l2.name} (Rs.19,500 expected revenue)")

        cr.commit()
        print("=" * 70)
        print("SUCCESS! ALL ROOMS PUBLISHED & WEBSITE LEADS GENERATED!")
        print("=" * 70)

if __name__ == '__main__':
    publish_rooms_and_setup_leads()
