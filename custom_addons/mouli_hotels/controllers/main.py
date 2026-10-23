# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

class HotelWebsiteController(http.Controller):

    @http.route(['/rooms', '/hotel/rooms'], type='http', auth='public', website=True, sitemap=True)
    def hotel_rooms(self, property_id=None, room_type_id=None, capacity=None, check_in=None, check_out=None, sort=None, **kw):
        """Public catalog of hotel room types with filters and instant lead capture."""
        RoomType = request.env['hotel.room.type'].sudo()
        Property = request.env['hotel.property'].sudo()

        # Target active properties
        properties = Property.search([])
        selected_property = None
        if property_id:
            try:
                selected_property = Property.browse(int(property_id))
            except (ValueError, TypeError):
                selected_property = None
        if not selected_property and properties:
            # Default to RB Resorts if present, otherwise first property
            rb = properties.filtered(lambda p: 'RB' in (p.name or ''))
            selected_property = rb[0] if rb else properties[0]

        # Domain for published room types
        domain = [('is_published', '=', True)]
        if capacity:
            try:
                domain.append(('capacity', '>=', int(capacity)))
            except (ValueError, TypeError):
                pass

        order = 'website_sequence asc, list_price asc, id asc'
        if sort == 'price_asc':
            order = 'list_price asc'
        elif sort == 'price_desc':
            order = 'list_price desc'
        elif sort == 'capacity_desc':
            order = 'capacity desc'

        room_types = RoomType.search(domain, order=order)

        # Pre-calculated dates for UI (Tomorrow -> +3 days)
        today = datetime.now().date()
        default_checkin = today + timedelta(days=1)
        default_checkout = today + timedelta(days=4)

        values = {
            'room_types': room_types,
            'properties': properties,
            'selected_property': selected_property,
            'selected_capacity': int(capacity) if capacity else None,
            'check_in': check_in or default_checkin.strftime('%Y-%m-%d'),
            'check_out': check_out or default_checkout.strftime('%Y-%m-%d'),
            'sort_order': sort,
        }
        return request.render('mouli_hotels.hotel_rooms_page', values)

    @http.route(['/rooms/<int:room_type_id>'], type='http', auth='public', website=True, sitemap=True)
    def hotel_room_detail(self, room_type_id, **kw):
        """Detailed luxury view of a specific room type with dedicated inquiry form."""
        RoomType = request.env['hotel.room.type'].sudo()
        Property = request.env['hotel.property'].sudo()

        room_type = RoomType.browse(room_type_id)
        if not room_type.exists() or not room_type.is_published:
            return request.redirect('/rooms')

        properties = Property.search([])
        rb = properties.filtered(lambda p: 'RB' in (p.name or ''))
        default_property = rb[0] if rb else (properties[0] if properties else None)

        other_rooms = RoomType.search([
            ('id', '!=', room_type.id),
            ('is_published', '=', True)
        ], limit=3, order='website_sequence asc')

        today = datetime.now().date()
        default_checkin = today + timedelta(days=1)
        default_checkout = today + timedelta(days=3)

        values = {
            'room_type': room_type,
            'properties': properties,
            'default_property': default_property,
            'other_rooms': other_rooms,
            'check_in': default_checkin.strftime('%Y-%m-%d'),
            'check_out': default_checkout.strftime('%Y-%m-%d'),
        }
        return request.render('mouli_hotels.hotel_room_detail_page', values)

    @http.route(['/rooms/inquiry/submit'], type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def submit_room_inquiry(self, **post):
        """
        Receives website lead / room inquiry.
        Creates CRM Lead + Draft Hotel Reservation + Links/Creates Guest Partner.
        """
        name = (post.get('guest_name') or '').strip()
        phone = (post.get('guest_phone') or '').strip()
        email = (post.get('guest_email') or '').strip()
        city = (post.get('guest_city') or '').strip()
        notes = (post.get('notes') or '').strip()
        meal_plan = post.get('meal_plan') or 'cp'

        try:
            room_type_id = int(post.get('room_type_id'))
            room_type = request.env['hotel.room.type'].sudo().browse(room_type_id)
        except (ValueError, TypeError):
            room_type = request.env['hotel.room.type'].sudo().search([('is_published', '=', True)], limit=1)

        try:
            property_id = int(post.get('property_id'))
            property_rec = request.env['hotel.property'].sudo().browse(property_id)
        except (ValueError, TypeError):
            property_rec = request.env['hotel.property'].sudo().search([('name', 'ilike', 'RB Resorts')], limit=1)
            if not property_rec:
                property_rec = request.env['hotel.property'].sudo().search([], limit=1)

        # Dates Parsing
        today = datetime.now().date()
        try:
            cin_date = datetime.strptime(post.get('check_in'), '%Y-%m-%d').date()
        except Exception:
            cin_date = today + timedelta(days=1)

        try:
            cout_date = datetime.strptime(post.get('check_out'), '%Y-%m-%d').date()
        except Exception:
            cout_date = cin_date + timedelta(days=2)

        if cout_date <= cin_date:
            cout_date = cin_date + timedelta(days=1)

        nights = (cout_date - cin_date).days or 1

        try:
            adults = max(1, int(post.get('adults', 1)))
        except (ValueError, TypeError):
            adults = 1

        try:
            children = max(0, int(post.get('children', 0)))
        except (ValueError, TypeError):
            children = 0

        rate_per_night = room_type.list_price if room_type else 3500.0
        estimated_total = rate_per_night * nights

        # 1. Partner Management
        Partner = request.env['res.partner'].sudo()
        partner = False
        if email:
            partner = Partner.search([('email', '=ilike', email)], limit=1)
        if not partner and phone:
            partner = Partner.search([('phone', '=', phone)], limit=1)

        if not partner:
            partner_vals = {
                'name': name or 'Online Guest Inquiry',
                'phone': phone,
                'email': email,
                'city': city,
                'is_hotel_guest': True,
                'vip_status': 'standard',
            }
            partner = Partner.create(partner_vals)
        else:
            p_updates = {}
            if name and partner.name in ('Online Guest Inquiry', False):
                p_updates['name'] = name
            if phone and not partner.phone:
                p_updates['phone'] = phone
            if email and not partner.email:
                p_updates['email'] = email
            if city and not partner.city:
                p_updates['city'] = city
            if p_updates:
                partner.write(p_updates)

        # 2. CRM Lead Creation
        Lead = request.env['crm.lead'].sudo()
        meal_plan_labels = {
            'ep': 'EP - Room Only',
            'cp': 'CP - Bed & Breakfast (Complimentary)',
            'map': 'MAP - Half Board (Breakfast + Dinner)',
            'ap': 'AP - Full Board (All Meals Included)',
        }
        lead_summary = f"""--- RESORT WEBSITE ROOM INQUIRY ---
Room Type: {room_type.name if room_type else 'General'}
Property: {property_rec.name if property_rec else 'RB Luxury Beach Resort & Spa'}
Dates: {cin_date.strftime('%d-%b-%Y')} to {cout_date.strftime('%d-%b-%Y')} ({nights} Nights)
Guests: {adults} Adults, {children} Children
Meal Plan: {meal_plan_labels.get(meal_plan, meal_plan)}
Estimated Room Revenue: ₹{estimated_total:,.2f}
Guest City: {city or 'Not Specified'}
Special Requests: {notes or 'None'}
"""
        lead_vals = {
            'name': f"Room Lead: {room_type.name if room_type else 'Suite'} - {name or phone}",
            'partner_id': partner.id,
            'contact_name': name,
            'phone': phone,
            'email_from': email,
            'city': city,
            'expected_revenue': estimated_total,
            'type': 'opportunity',
            'description': lead_summary,
            'priority': '2',
        }
        lead = Lead.create(lead_vals)

        # Tag CRM Lead
        try:
            Tag = request.env['crm.tag'].sudo()
            tag_web = Tag.search([('name', '=', 'Website Room Lead')], limit=1)
            if not tag_web:
                tag_web = Tag.create({'name': 'Website Room Lead', 'color': 4})
            lead.write({'tag_ids': [(4, tag_web.id)]})
        except Exception as e:
            _logger.warning("Could not set CRM tag: %s", e)

        # 3. Create Draft Hotel Reservation
        Reservation = request.env['hotel.reservation'].sudo()
        check_in_dt = datetime.combine(cin_date, datetime.strptime("14:00:00", "%H:%M:%S").time())
        check_out_dt = datetime.combine(cout_date, datetime.strptime("11:00:00", "%H:%M:%S").time())

        res_vals = {
            'guest_id': partner.id,
            'property_id': property_rec.id if property_rec else False,
            'room_type_id': room_type.id if room_type else False,
            'check_in': check_in_dt,
            'check_out': check_out_dt,
            'adults': adults,
            'children': children,
            'meal_plan': meal_plan,
            'rate_per_night': rate_per_night,
            'state': 'draft', # Draft reservation ready for Front Desk review & confirmation
            'booking_source': 'website',
            'crm_lead_id': lead.id,
            'dietary_notes': f"Website Inquiry for {meal_plan.upper()} meal plan.",
            'notes': f"Website Web Lead #{lead.id}. Special Requests: {notes}" if notes else f"Website Web Lead #{lead.id}.",
        }
        reservation = Reservation.create(res_vals)

        _logger.info("Successfully generated website room lead: Lead ID %s, Res ID %s for %s", lead.id, reservation.id, name)

        return request.redirect(f'/rooms/inquiry/success?res_id={reservation.id}&lead_id={lead.id}')

    @http.route(['/rooms/inquiry/success'], type='http', auth='public', website=True)
    def inquiry_success(self, res_id=None, lead_id=None, **kw):
        """Displays positive confirmation with WhatsApp chat and call actions."""
        reservation = None
        lead = None
        if res_id:
            try:
                reservation = request.env['hotel.reservation'].sudo().browse(int(res_id))
            except Exception:
                reservation = None

        if lead_id:
            try:
                lead = request.env['crm.lead'].sudo().browse(int(lead_id))
            except Exception:
                lead = None

        # Build WhatsApp message
        property_name = reservation.property_id.name if reservation and reservation.property_id else "RB Luxury Beach Resort & Spa"
        room_name = reservation.room_type_id.name if reservation and reservation.room_type_id else "Luxury Room"
        ref_code = reservation.name if reservation else (f"LEAD-{lead.id}" if lead else "WEB-INQUIRY")
        
        wa_text = f"Hello {property_name}! I just submitted online room inquiry {ref_code} for {room_name}. Please share confirmation and payment details."
        import urllib.parse
        encoded_wa = urllib.parse.quote(wa_text)

        values = {
            'reservation': reservation,
            'lead': lead,
            'property_name': property_name,
            'ref_code': ref_code,
            'encoded_wa_msg': encoded_wa,
            'resort_phone': reservation.property_id.phone if reservation and reservation.property_id and reservation.property_id.phone else "+91 891 285 4500",
        }
        return request.render('mouli_hotels.hotel_room_inquiry_success', values)
