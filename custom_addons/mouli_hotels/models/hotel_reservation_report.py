# -*- coding: utf-8 -*-
from odoo import models, fields, tools

class HotelReservationReport(models.Model):
    _name = 'hotel.reservation.report'
    _description = 'Hotel Reservation & Revenue Analytics'
    _auto = False
    _order = 'check_in desc'

    # Dimensions
    reservation_id = fields.Many2one('hotel.reservation', string='Reservation', readonly=True)
    name = fields.Char(string='Reservation No', readonly=True)
    property_id = fields.Many2one('hotel.property', string='Property / Resort', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    guest_id = fields.Many2one('res.partner', string='Guest', readonly=True)
    guest_vip = fields.Selection([
        ('standard', 'Standard'),
        ('silver', 'Silver VIP'),
        ('gold', 'Gold VIP'),
        ('platinum', 'Platinum VIP'),
        ('diamond', 'Diamond VIP')
    ], string='VIP Status', readonly=True)
    room_type_id = fields.Many2one('hotel.room.type', string='Room Type', readonly=True)
    room_id = fields.Many2one('hotel.room', string='Room', readonly=True)
    booking_source = fields.Selection([
        ('direct', 'Direct / Walk-In'),
        ('phone', 'Phone / Inquiry'),
        ('website', 'Hotel Website'),
        ('ota', 'OTA (Booking.com / Expedia)')
    ], string='Booking Source / Channel', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('check_in', 'Checked In'),
        ('check_out', 'Checked Out'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True)

    # Dates
    check_in = fields.Datetime(string='Check-In Date', readonly=True)
    check_out = fields.Datetime(string='Check-Out Date', readonly=True)
    booking_date = fields.Datetime(string='Booking Date', readonly=True)

    # Measures
    nights = fields.Integer(string='Nights', readonly=True)
    adults = fields.Integer(string='Adults', readonly=True)
    children = fields.Integer(string='Children', readonly=True)
    rate_per_night = fields.Monetary(string='Rate / Night', readonly=True, currency_field='currency_id')
    amount_total = fields.Monetary(string='Total Revenue', readonly=True, currency_field='currency_id')
    amount_paid = fields.Monetary(string='Amount Paid', readonly=True, currency_field='currency_id')
    amount_due = fields.Monetary(string='Balance Due', readonly=True, currency_field='currency_id')
    adr = fields.Monetary(string='ADR (Avg Daily Rate)', readonly=True, currency_field='currency_id')
    lead_time_days = fields.Integer(string='Lead Time (Days)', readonly=True)
    res_count = fields.Integer(string='Bookings Count', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE or REPLACE VIEW {self._table} AS (
                SELECT
                    r.id as id,
                    r.id as reservation_id,
                    r.name as name,
                    r.property_id as property_id,
                    r.company_id as company_id,
                    c.currency_id as currency_id,
                    r.guest_id as guest_id,
                    COALESCE(p.vip_status, 'standard') as guest_vip,
                    r.room_type_id as room_type_id,
                    r.room_id as room_id,
                    r.booking_source as booking_source,
                    r.state as state,
                    r.check_in as check_in,
                    r.check_out as check_out,
                    r.create_date as booking_date,
                    r.nights as nights,
                    r.adults as adults,
                    r.children as children,
                    r.rate_per_night as rate_per_night,
                    r.amount_total as amount_total,
                    COALESCE(f.amount_paid, r.advance_payment, 0.0) as amount_paid,
                    COALESCE(f.amount_due, r.amount_total - COALESCE(r.advance_payment, 0.0), 0.0) as amount_due,
                    CASE 
                        WHEN r.nights > 0 THEN r.amount_total / r.nights 
                        ELSE r.rate_per_night 
                    END as adr,
                    GREATEST(0, EXTRACT(DAY FROM (r.check_in - r.create_date)))::INTEGER as lead_time_days,
                    1 as res_count
                FROM
                    hotel_reservation r
                    LEFT JOIN res_company c ON r.company_id = c.id
                    LEFT JOIN res_partner p ON r.guest_id = p.id
                    LEFT JOIN hotel_folio f ON r.folio_id = f.id
            )
        """)
