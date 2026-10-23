# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _description = 'Hotel Room Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'check_in desc, id desc'

    name = fields.Char(string='Reservation No', copy=False, readonly=True, default=lambda self: _('New'))
    property_id = fields.Many2one('hotel.property', string='Property', required=True, tracking=True)
    company_id = fields.Many2one('res.company', related='property_id.company_id', string='Company', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency', readonly=True)

    guest_id = fields.Many2one('res.partner', string='Guest Name', required=True, tracking=True)
    room_type_id = fields.Many2one('hotel.room.type', string='Room Type', required=True, tracking=True)
    room_id = fields.Many2one(
        'hotel.room', string='Assigned Room', tracking=True,
        domain="[('property_id', '=', property_id), ('room_type_id', '=', room_type_id)]"
    )

    check_in = fields.Datetime(string='Check-In Date', required=True, tracking=True)
    check_out = fields.Datetime(string='Check-Out Date', required=True, tracking=True)
    nights = fields.Integer(string='Nights', compute='_compute_nights', store=True)

    adults = fields.Integer(string='Adults', default=1, required=True)
    children = fields.Integer(string='Children', default=0)

    rate_per_night = fields.Monetary(string='Rate / Night', currency_field='currency_id', tracking=True)
    amount_total = fields.Monetary(string='Total Amount', compute='_compute_amount_total', store=True, currency_field='currency_id')

    # Advance Payment Policy
    advance_payment = fields.Monetary(
        string='Advance Deposit', currency_field='currency_id', tracking=True,
        help="Advance payment required to confirm the room booking."
    )
    advance_payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit / Debit Card'),
        ('upi', 'UPI / QR / Online'),
        ('bank', 'Bank Transfer')
    ], string='Advance Payment Mode', default='cash')
    advance_payment_ref = fields.Char(string='Advance Txn / Receipt Ref')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('check_in', 'Checked In'),
        ('check_out', 'Checked Out'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    booking_source = fields.Selection([
        ('direct', 'Direct / Walk-In'),
        ('phone', 'Phone / Inquiry'),
        ('website', 'Hotel Website'),
        ('ota', 'OTA (Booking.com / Expedia)')
    ], string='Booking Source', default='direct')

    crm_lead_id = fields.Many2one('crm.lead', string='Source CRM Lead', readonly=True, copy=False)
    folio_id = fields.Many2one('hotel.folio', string='Guest Folio', readonly=True, copy=False)
    amount_paid = fields.Monetary(related='folio_id.amount_paid', string='Total Paid', readonly=True)
    amount_due = fields.Monetary(related='folio_id.amount_due', string='Balance Due', readonly=True)
    payment_status = fields.Selection(
        related='folio_id.payment_status', string='Payment Status', readonly=True
    )

    # Meal Plan & Breakfast Entitlement
    meal_plan = fields.Selection([
        ('ep', 'EP - European Plan (Room Only)'),
        ('cp', 'CP - Continental Plan (Breakfast Included)'),
        ('map', 'MAP - Half Board (Breakfast + Dinner)'),
        ('ap', 'AP - Full Board (All Meals Included)')
    ], string='Meal Plan', default='cp', tracking=True,
       help="EP: Room Only | CP: Bed & Breakfast | MAP: Breakfast + Dinner | AP: All Meals Included")
    breakfast_entitlement = fields.Selection([
        ('included', 'Included (Complimentary)'),
        ('chargeable', 'Chargeable'),
    ], string='Breakfast Status', compute='_compute_breakfast_entitlement', store=True)
    dietary_notes = fields.Char(string='Dietary / Breakfast Notes', help="Vegetarian, Jain, Vegan, Food Allergies, etc.")
    breakfast_item_ids = fields.Many2many('hotel.breakfast.item', string='Preferred Breakfast Items')
    total_guests = fields.Integer(string='Total Covers (Guests)', compute='_compute_total_guests', store=True)

    # VIP Status
    vip_status = fields.Selection(related='guest_id.vip_status', string='VIP Status', store=True)
    is_vip = fields.Boolean(string='Is VIP', compute='_compute_is_vip', store=True)

    notes = fields.Text(string='Special Requests / Notes')

    @api.depends('meal_plan')
    def _compute_breakfast_entitlement(self):
        for rec in self:
            if rec.meal_plan in ('cp', 'map', 'ap'):
                rec.breakfast_entitlement = 'included'
            else:
                rec.breakfast_entitlement = 'chargeable'

    @api.depends('adults', 'children')
    def _compute_total_guests(self):
        for rec in self:
            rec.total_guests = (rec.adults or 0) + (rec.children or 0)

    @api.depends('vip_status')
    def _compute_is_vip(self):
        for rec in self:
            rec.is_vip = bool(rec.vip_status and rec.vip_status in ('silver', 'gold', 'platinum'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hotel.reservation') or _('New')
            if vals.get('guest_id'):
                # Ensure partner is flagged as hotel guest
                self.env['res.partner'].browse(vals['guest_id']).write({'is_hotel_guest': True})
        return super().create(vals_list)

    @api.onchange('room_type_id')
    def _onchange_room_type(self):
        if self.room_type_id and not self.rate_per_night:
            self.rate_per_night = self.room_type_id.list_price
        if self.room_id and self.room_id.room_type_id != self.room_type_id:
            self.room_id = False

    @api.depends('check_in', 'check_out')
    def _compute_nights(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                diff = (rec.check_out.date() - rec.check_in.date()).days
                rec.nights = max(1, diff)
            else:
                rec.nights = 1

    @api.depends('nights', 'rate_per_night')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = (rec.nights or 1) * (rec.rate_per_night or 0.0)

    @api.constrains('check_in', 'check_out', 'room_id', 'state')
    def _check_room_availability(self):
        for rec in self:
            if rec.check_in and rec.check_out and rec.check_out <= rec.check_in:
                raise ValidationError(_("Check-out date must be strictly after Check-in date!"))

            if rec.room_id and rec.state in ('confirmed', 'check_in'):
                # Check for overlapping active reservations on the same physical room
                overlapping = self.search([
                    ('id', '!=', rec.id),
                    ('room_id', '=', rec.room_id.id),
                    ('state', 'in', ('confirmed', 'check_in')),
                    ('check_in', '<', rec.check_out),
                    ('check_out', '>', rec.check_in),
                ])
                if overlapping:
                    other = overlapping[0]
                    raise ValidationError(_(
                        "Double-Booking Conflict: Room %s is already reserved under %s from %s to %s."
                    ) % (rec.room_id.name, other.name, other.check_in, other.check_out))

    def action_confirm(self):
        for rec in self:
            if not rec.room_id:
                # Find first available room of this type
                available_rooms = self.env['hotel.room'].search([
                    ('property_id', '=', rec.property_id.id),
                    ('room_type_id', '=', rec.room_type_id.id),
                    ('active', '=', True),
                    ('maintenance_status', '=', 'operational'),
                ])
                for candidate in available_rooms:
                    overlap = self.search([
                        ('room_id', '=', candidate.id),
                        ('state', 'in', ('confirmed', 'check_in')),
                        ('check_in', '<', rec.check_out),
                        ('check_out', '>', rec.check_in),
                    ])
                    if not overlap:
                        rec.room_id = candidate.id
                        break
            if rec.room_id:
                rec.room_id.write({'occupancy_status': 'reserved'})
            rec.write({'state': 'confirmed'})

    def action_check_in(self):
        for rec in self:
            if not rec.room_id:
                raise ValidationError(_("Please assign a physical room before check-in."))
            # Auto-mark room clean if not already inspected/clean for front-desk speed
            if rec.room_id.housekeeping_status not in ('clean', 'inspected'):
                rec.room_id.write({'housekeeping_status': 'clean'})

            rec.room_id.write({
                'occupancy_status': 'occupied',
                'current_reservation_id': rec.id,
            })

            # Create Folio automatically if not present
            rec._ensure_folio()
            rec.write({'state': 'check_in'})

    def _ensure_folio(self):
        self.ensure_one()
        if not self.folio_id:
            folio = self.env['hotel.folio'].create({
                'reservation_id': self.id,
                'guest_id': self.guest_id.id,
                'room_id': self.room_id.id if self.room_id else False,
                'property_id': self.property_id.id,
            })
            if self.room_id:
                self.env['hotel.folio.line'].create({
                    'folio_id': folio.id,
                    'name': f"Room Stay: {self.room_id.name} ({self.nights} Nights)",
                    'service_type': 'room',
                    'quantity': self.nights,
                    'price_unit': self.rate_per_night,
                })
            if self.advance_payment and self.advance_payment > 0:
                self.env['hotel.folio.payment'].create({
                    'folio_id': folio.id,
                    'name': f"Advance Deposit for {self.name}",
                    'amount': self.advance_payment,
                    'payment_method': self.advance_payment_method or 'cash',
                    'reference': self.advance_payment_ref or 'Booking Advance',
                    'is_advance': True,
                })
            self.folio_id = folio.id
        return self.folio_id

    def action_check_out(self):
        self.ensure_one()
        # If there is an outstanding balance, open the 1-Click Quick Settle & Checkout Wizard!
        if self.folio_id and self.folio_id.amount_due > 0.01:
            return {
                'name': _('Quick Settle & Check Out (%s)') % self.name,
                'type': 'ir.actions.act_window',
                'res_model': 'hotel.quick.checkout.wizard',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'target': 'new',
                'context': {
                    'active_id': self.id,
                    'active_model': 'hotel.reservation',
                    'default_reservation_id': self.id,
                    'default_payment_amount': self.folio_id.amount_due,
                }
            }
        # If already fully settled or 0 due, complete checkout directly
        self._execute_checkout()
        return True

    def _execute_checkout(self):
        for rec in self:
            if rec.folio_id:
                rec.folio_id.write({'state': 'paid'})

            if rec.room_id:
                rec.room_id.write({
                    'occupancy_status': 'vacant',
                    'housekeeping_status': 'dirty',
                    'current_reservation_id': False,
                })
                # Automatically trigger a Housekeeping Task for cleaning
                self.env['hotel.housekeeping.task'].create({
                    'room_id': rec.room_id.id,
                    'task_type': 'checkout_clean',
                    'scheduled_date': fields.Date.context_today(self),
                    'priority': '2',
                    'notes': f"Guest {rec.guest_id.name} checked out from {rec.name}. Room vacated.",
                })

            rec.write({'state': 'check_out'})

    def action_register_payment(self):
        self.ensure_one()
        folio = self._ensure_folio()
        return folio.action_register_payment()

    def action_print_bill(self):
        self.ensure_one()
        folio = self._ensure_folio()
        return folio.action_print_bill()

    def action_cancel(self):
        for rec in self:
            if rec.room_id and rec.room_id.current_reservation_id == rec:
                rec.room_id.write({
                    'occupancy_status': 'vacant',
                    'current_reservation_id': False,
                })
            rec.write({'state': 'cancel'})

    def action_view_folio(self):
        self.ensure_one()
        folio = self._ensure_folio()
        return {
            'name': 'Guest Folio',
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.folio',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': folio.id,
            'target': 'current',
        }

    @api.model
    def search_tape_chart_guests(self, query=None, property_id=None, **kwargs):
        """
        Global search for guests across all reservations:
        Matches guest name, reservation number, room number, or guest phone.
        Includes all reservation statuses (In-House, Checked-Out, Confirmed, etc.).
        Returns detailed list of matching stays even if the same guest repeats.
        """
        if not query or len(str(query).strip()) < 1:
            return []

        search_str = str(query).strip()
        domain = [
            '|', '|', '|',
            ('guest_id.name', 'ilike', search_str),
            ('name', 'ilike', search_str),
            ('room_id.room_number', 'ilike', search_str),
            ('guest_id.phone', 'ilike', search_str),
        ]
        if property_id:
            domain.append(('property_id', '=', int(property_id)))

        # Find all matching reservations (including past check-outs and repeated stays!)
        reservations = self.search(domain, order='check_in desc', limit=50)
        results = []
        for r in reservations:
            check_in_date = r.check_in.date() if r.check_in else None
            check_out_date = r.check_out.date() if r.check_out else None
            currency_symbol = r.currency_id.symbol if r.currency_id else '₹'
            status_style = 'occupied'
            if r.state == 'confirmed':
                status_style = 'reserved'
            elif r.state == 'check_out':
                status_style = 'checked_out'
            elif r.state == 'cancel':
                status_style = 'cancelled'

            results.append({
                'id': r.id,
                'name': r.name,
                'guest_name': r.guest_id.name or 'Unnamed Guest',
                'guest_phone': r.guest_id.phone or getattr(r.guest_id, 'mobile', '') or '',
                'guest_email': r.guest_id.email or '',
                'guest_vip': r.guest_id.vip_status or 'standard',
                'room_id': r.room_id.id if r.room_id else False,
                'room_number': r.room_id.room_number if r.room_id else 'Unassigned',
                'room_name': r.room_id.name if r.room_id else 'No Room Assigned',
                'room_type_name': r.room_id.room_type_id.name if r.room_id and r.room_id.room_type_id else '',
                'property_id': r.property_id.id if r.property_id else False,
                'property_name': r.property_id.name if r.property_id else '',
                'check_in': check_in_date.strftime('%Y-%m-%d') if check_in_date else '',
                'check_in_display': r.check_in.strftime('%d %b %Y') if r.check_in else '',
                'check_in_dt': r.check_in.strftime('%d %b %Y, %I:%M %p') if r.check_in else '',
                'check_out': check_out_date.strftime('%Y-%m-%d') if check_out_date else '',
                'check_out_display': r.check_out.strftime('%d %b %Y') if r.check_out else '',
                'check_out_dt': r.check_out.strftime('%d %b %Y, %I:%M %p') if r.check_out else '',
                'nights': r.nights,
                'adults': r.adults,
                'children': r.children,
                'state': r.state,
                'status_style': status_style,
                'state_label': dict(r._fields['state'].selection).get(r.state, r.state.title()),
                'rate_per_night': r.rate_per_night,
                'rate_formatted': f"{currency_symbol}{r.rate_per_night:,.2f}",
                'amount_total': r.amount_total,
                'total_formatted': f"{currency_symbol}{r.amount_total:,.2f}",
                'amount_paid': r.amount_paid,
                'paid_formatted': f"{currency_symbol}{r.amount_paid:,.2f}",
                'amount_due': r.amount_due,
                'due_formatted': f"{currency_symbol}{r.amount_due:,.2f}",
                'folio_id': r.folio_id.id if r.folio_id else False,
                'booking_source': dict(r._fields['booking_source'].selection).get(r.booking_source, 'Direct') if r.booking_source else 'Direct',
                'notes': r.notes or '',
            })
        return results

    @api.model
    def get_tape_chart_data(self, start_date_str=None, days_count=11, property_id=None, group_by='room_type', meal_plan='CP', start_date=None, **kwargs):
        """
        High-performance backend API for Hotel Tape Chart / Reservation Grid Calendar.
        Matches industry standard PMS (Opera, Cloudbeds, eZee).
        """
        from datetime import datetime, date, timedelta

        # Parse anchor start date
        raw_date = start_date_str or start_date
        if raw_date:
            try:
                start_date = datetime.strptime(str(raw_date)[:10], '%Y-%m-%d').date()
            except Exception:
                start_date = date.today()
        else:
            start_date = date.today()

        days_count = max(7, min(31, int(days_count or 11)))
        today = date.today()
        end_date = start_date + timedelta(days=days_count)

        # Build Days Header List
        days_header = []
        for i in range(days_count):
            cur_date = start_date + timedelta(days=i)
            days_header.append({
                'index': i,
                'date': cur_date.strftime('%Y-%m-%d'),
                'day_name': cur_date.strftime('%a').upper(),
                'day_number': cur_date.day,
                'month_name': cur_date.strftime('%b'),
                'is_today': (cur_date == today),
                'is_weekend': (cur_date.weekday() in (5, 6)),
            })

        # Property scope
        Property = self.env['hotel.property']
        if property_id:
            props = Property.browse(int(property_id))
        else:
            all_active_props = Property.search([('active', '=', True)])
            props = all_active_props.sorted(lambda p: len(p.room_ids), reverse=True)[:1]
            if not props:
                props = Property.search([], limit=1)

        prop_domain = [('property_id', '=', props.id)] if props else []
        all_rooms = self.env['hotel.room'].search(prop_domain + [('active', '=', True)], order='room_number')
        all_props = [{'id': p.id, 'name': p.name, 'code': p.code} for p in Property.search([('active', '=', True)])]
        currency = (props.currency_id if props and hasattr(props, 'currency_id') and props.currency_id else self.env.company.currency_id)
        currency_symbol = currency.symbol if currency else '$'

        # Top KPI Metrics (for today)
        vacant_rooms = all_rooms.filtered(lambda r: r.occupancy_status == 'vacant' and r.maintenance_status == 'operational')
        occupied_rooms = all_rooms.filtered(lambda r: r.occupancy_status == 'occupied')
        reserved_rooms = all_rooms.filtered(lambda r: r.occupancy_status == 'reserved')
        blocked_rooms = all_rooms.filtered(lambda r: r.maintenance_status in ('maintenance', 'out_of_service'))
        dirty_rooms = all_rooms.filtered(lambda r: r.housekeeping_status in ('dirty', 'cleaning'))

        # Today's checkouts (due out)
        due_out_res = self.search([
            ('property_id', '=', props.id if props else False),
            ('state', '=', 'check_in'),
            ('check_out', '>=', datetime.combine(today, datetime.min.time())),
            ('check_out', '<=', datetime.combine(today, datetime.max.time())),
        ])

        metrics = {
            'all': len(all_rooms),
            'vacant': len(vacant_rooms),
            'occupied': len(occupied_rooms),
            'reserved': len(reserved_rooms),
            'blocked': len(blocked_rooms),
            'due_out': len(due_out_res),
            'dirty': len(dirty_rooms),
        }

        # Fetch all overlapping reservations within the date window
        window_start_dt = datetime.combine(start_date, datetime.min.time())
        window_end_dt = datetime.combine(end_date, datetime.max.time())

        reservations = self.search([
            ('property_id', '=', props.id if props else False),
            ('state', 'in', ('confirmed', 'check_in', 'check_out')),
            ('check_in', '<', window_end_dt),
            ('check_out', '>', window_start_dt),
        ])

        # Meal Plan rate adjustments
        plan_multiplier = 1.0
        plan_delta = 0.0
        if meal_plan == 'EP':
            plan_delta = -200.0
        elif meal_plan == 'MAP':
            plan_delta = 800.0
        elif meal_plan == 'AP':
            plan_delta = 1500.0
        # CP is base rate with breakfast included

        # Grouping logic (Room Type / Floor / Building)
        groups_dict = {}
        room_types = self.env['hotel.room.type'].search([])
        for rt in room_types:
            groups_dict[rt.id] = {
                'id': rt.id,
                'name': rt.name.upper(),
                'code': rt.code,
                'base_price': rt.list_price,
                'rooms': [],
                'daily_info': [],
            }

        for rm in all_rooms:
            rt_id = rm.room_type_id.id
            if rt_id not in groups_dict:
                groups_dict[rt_id] = {
                    'id': rt_id,
                    'name': rm.room_type_id.name.upper() if rm.room_type_id else 'STANDARD ROOMS',
                    'code': rm.room_type_id.code if rm.room_type_id else 'STD',
                    'base_price': rm.list_price or 2000.0,
                    'rooms': [],
                    'daily_info': [],
                }
            
            # Find bookings on this specific physical room
            room_bookings = []
            rm_reservations = reservations.filtered(lambda r: r.room_id.id == rm.id)
            currency_symbol = props.currency_id.symbol if (props and props.currency_id) else '₹'
            for res in rm_reservations:
                res_in = res.check_in.date()
                res_out = res.check_out.date()
                
                # Column bounds
                start_col = max(0, (res_in - start_date).days)
                end_col = min(days_count, (res_out - start_date).days)
                col_span = max(1, end_col - start_col)

                if start_col < days_count and end_col > 0:
                    status_style = 'occupied'
                    if res.state == 'confirmed':
                        status_style = 'reserved'
                    elif res.state == 'check_out':
                        status_style = 'checked_out'

                    guest_display_name = res.guest_id.name or res.name or _('Guest')
                    room_bookings.append({
                        'id': res.id,
                        'name': res.name,
                        'guest_name': guest_display_name,
                        'guest_phone': res.guest_id.phone or getattr(res.guest_id, 'mobile', '') or '',
                        'guest_email': res.guest_id.email or '',
                        'guest_vip': res.guest_id.vip_status or 'standard',
                        'start_col': start_col,
                        'col_span': col_span,
                        'state': res.state,
                        'status_style': status_style,
                        'check_in': res_in.strftime('%Y-%m-%d'),
                        'check_out': res_out.strftime('%Y-%m-%d'),
                        'check_in_dt': res.check_in.strftime('%d %b %Y, %I:%M %p') if res.check_in else '',
                        'check_out_dt': res.check_out.strftime('%d %b %Y, %I:%M %p') if res.check_out else '',
                        'nights': res.nights,
                        'adults': res.adults,
                        'children': res.children,
                        'rate_per_night': res.rate_per_night,
                        'rate_formatted': f"{currency_symbol}{res.rate_per_night:,.2f}",
                        'amount_total': res.amount_total,
                        'total_formatted': f"{currency_symbol}{res.amount_total:,.2f}",
                        'amount_paid': res.amount_paid,
                        'paid_formatted': f"{currency_symbol}{res.amount_paid:,.2f}",
                        'amount_due': res.amount_due,
                        'due_formatted': f"{currency_symbol}{res.amount_due:,.2f}",
                        'folio_id': res.folio_id.id if res.folio_id else False,
                        'booking_source': dict(res._fields['booking_source'].selection).get(res.booking_source, 'Direct') if res.booking_source else 'Direct',
                        'notes': res.notes or '',
                        'room_number': rm.room_number,
                        'room_type_name': rm.room_type_id.name if rm.room_type_id else '',
                    })

            # Check if room is in maintenance
            if rm.maintenance_status in ('maintenance', 'out_of_service'):
                room_bookings.append({
                    'id': False,
                    'name': 'MAINTENANCE',
                    'guest_name': 'Under Maintenance',
                    'guest_phone': '',
                    'guest_email': '',
                    'guest_vip': 'none',
                    'start_col': 0,
                    'col_span': days_count,
                    'state': 'maintenance',
                    'status_style': 'maintenance',
                    'check_in': start_date.strftime('%Y-%m-%d'),
                    'check_out': end_date.strftime('%Y-%m-%d'),
                    'check_in_dt': start_date.strftime('%d %b %Y'),
                    'check_out_dt': end_date.strftime('%d %b %Y'),
                    'nights': days_count,
                    'adults': 0,
                    'children': 0,
                    'rate_per_night': 0.0,
                    'rate_formatted': f"{currency_symbol}0.00",
                    'amount_total': 0.0,
                    'total_formatted': f"{currency_symbol}0.00",
                    'amount_paid': 0.0,
                    'paid_formatted': f"{currency_symbol}0.00",
                    'amount_due': 0.0,
                    'due_formatted': f"{currency_symbol}0.00",
                    'folio_id': False,
                    'booking_source': 'Internal',
                    'notes': 'Room is out of service for repairs or maintenance.',
                    'room_number': rm.room_number,
                    'room_type_name': rm.room_type_id.name if rm.room_type_id else '',
                })

            groups_dict[rt_id]['rooms'].append({
                'id': rm.id,
                'number': rm.room_number,
                'name': rm.name,
                'floor': rm.floor_id.name if rm.floor_id else '',
                'occupancy_status': rm.occupancy_status,
                'housekeeping_status': rm.housekeeping_status,
                'maintenance_status': rm.maintenance_status,
                'bookings': room_bookings,
            })

        # Calculate daily inventory & rates per group
        total_rooms_count = len(all_rooms)
        daily_available_overall = [0] * days_count
        daily_occupied_overall = [0] * days_count

        result_groups = []
        for g_id, group in groups_dict.items():
            if not group['rooms']:
                continue
            
            group_rooms = group['rooms']
            group_total_rooms = len(group_rooms)

            daily_info = []
            for d in range(days_count):
                day_date = start_date + timedelta(days=d)

                # Count occupied / blocked rooms in this group on day_date
                busy_count = 0
                for r in group_rooms:
                    is_busy = False
                    for b in r['bookings']:
                        if b['start_col'] <= d < (b['start_col'] + b['col_span']):
                            is_busy = True
                            break
                    if is_busy:
                        busy_count += 1

                avail = max(0, group_total_rooms - busy_count)
                daily_available_overall[d] += avail
                daily_occupied_overall[d] += busy_count

                # Dynamic rate calculation
                adj_price = max(500.0, group['base_price'] + plan_delta)
                # Weekend slight rate boost (e.g. 500 extra on Fri & Sat)
                if day_date.weekday() in (4, 5):  # Fri / Sat
                    adj_price += 500.0

                daily_info.append({
                    'date': day_date.strftime('%Y-%m-%d'),
                    'available_count': avail,
                    'price_formatted': f"{currency_symbol}{adj_price:,.0f}",
                    'is_sold_out': (avail == 0),
                })

            group['daily_info'] = daily_info
            result_groups.append(group)

        # Bottom Occupancy % calculations
        occupancy_percents = []
        for d in range(days_count):
            if total_rooms_count > 0:
                occ_pct = int(round((daily_occupied_overall[d] / total_rooms_count) * 100))
            else:
                occ_pct = 0
            occupancy_percents.append({
                'percent': occ_pct,
                'available': daily_available_overall[d],
                'occupied': daily_occupied_overall[d],
            })

        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'days_count': days_count,
            'days_header': days_header,
            'current_property': {
                'id': props.id if props else False,
                'name': props.name if props else 'All Properties',
                'code': props.code if props else '',
            },
            'all_properties': all_props,
            'metrics': metrics,
            'meal_plan': meal_plan,
            'currency_symbol': currency_symbol,
            'groups': result_groups,
            'all_room_types': [{'id': rt.id, 'name': rt.name, 'price': rt.list_price} for rt in room_types],
            'all_rooms_list': [{
                'id': rm.id,
                'number': rm.room_number,
                'name': rm.name,
                'room_type_id': rm.room_type_id.id,
                'room_type_name': rm.room_type_id.name or '',
                'list_price': rm.list_price
            } for rm in all_rooms],
            'bottom_summary': {
                'available_inventory': [d['available'] for d in occupancy_percents],
                'occupancy_percent': occupancy_percents,
            }
        }

    @api.model
    def quick_create_reservation(self, vals):
        """
        Streamlined API to create hotel reservation from Tape Chart UI in 1-click.
        """
        guest_name = (vals.get('guest_name') or '').strip()
        guest_phone = (vals.get('guest_phone') or '').strip()
        guest_email = (vals.get('guest_email') or '').strip()
        guest_id = vals.get('guest_id')

        if not guest_id and guest_name:
            domain = [('name', '=ilike', guest_name)]
            if guest_phone:
                domain = ['|', ('name', '=ilike', guest_name), ('phone', '=', guest_phone)]
            partner = self.env['res.partner'].search(domain, limit=1)
            if not partner:
                partner_vals = {
                    'name': guest_name,
                    'is_hotel_guest': True,
                }
                if guest_phone:
                    partner_vals['phone'] = guest_phone
                if guest_email:
                    partner_vals['email'] = guest_email
                partner = self.env['res.partner'].create(partner_vals)
            guest_id = partner.id

        if not guest_id:
            raise ValidationError(_("Please provide a valid Guest Name."))

        property_id = vals.get('property_id')
        room_id = vals.get('room_id')
        room_type_id = vals.get('room_type_id')

        if room_id and not room_type_id:
            room = self.env['hotel.room'].browse(int(room_id))
            room_type_id = room.room_type_id.id
            if not property_id:
                property_id = room.property_id.id

        if not property_id:
            props = self.env['hotel.property'].search([], limit=1)
            property_id = props.id if props else False

        check_in_str = vals.get('check_in')
        check_out_str = vals.get('check_out')
        if check_in_str and len(check_in_str) == 10:
            check_in_dt = f"{check_in_str} 14:00:00"
        else:
            check_in_dt = check_in_str

        if check_out_str and len(check_out_str) == 10:
            check_out_dt = f"{check_out_str} 11:00:00"
        else:
            check_out_dt = check_out_str

        res_vals = {
            'property_id': property_id,
            'guest_id': guest_id,
            'room_type_id': room_type_id,
            'room_id': room_id,
            'check_in': check_in_dt,
            'check_out': check_out_dt,
            'adults': int(vals.get('adults', 1)),
            'children': int(vals.get('children', 0)),
            'rate_per_night': float(vals.get('rate_per_night', 0.0)),
            'advance_payment': float(vals.get('advance_payment', 0.0)),
            'advance_payment_method': vals.get('advance_payment_method', 'cash'),
            'notes': vals.get('notes', ''),
            'booking_source': vals.get('booking_source', 'direct'),
        }

        reservation = self.create(res_vals)

        action_mode = vals.get('action_mode', 'confirm')
        if action_mode in ('confirm', 'check_in'):
            reservation.action_confirm()
            if action_mode == 'check_in':
                reservation.action_check_in()

        return {
            'id': reservation.id,
            'name': reservation.name,
            'guest_name': reservation.guest_id.name,
            'state': reservation.state,
        }

    @api.model
    def quick_update_room_status(self, room_id, status_type, new_status):
        """
        Quick status toggle for rooms (housekeeping or maintenance).
        """
        room = self.env['hotel.room'].browse(int(room_id))
        if not room.exists():
            return {'success': False, 'error': 'Room not found'}

        if status_type == 'housekeeping':
            if new_status in ('clean', 'dirty', 'cleaning', 'inspected'):
                room.write({'housekeeping_status': new_status})
        elif status_type == 'maintenance':
            if new_status in ('operational', 'maintenance', 'out_of_service'):
                room.write({'maintenance_status': new_status})

        return {
            'success': True,
            'room_id': room.id,
            'housekeeping_status': room.housekeeping_status,
            'maintenance_status': room.maintenance_status,
        }

    @api.model
    def search_guests(self, query=''):
        """
        Quick search for guests by name, phone or email.
        """
        domain = [('is_hotel_guest', '=', True)]
        if query:
            domain += ['|', '|', ('name', 'ilike', query), ('phone', 'ilike', query), ('email', 'ilike', query)]
        partners = self.env['res.partner'].search(domain, limit=12)
        return [{
            'id': p.id,
            'name': p.name,
            'phone': p.phone or getattr(p, 'mobile', '') or '',
            'email': p.email or ''
        } for p in partners]

