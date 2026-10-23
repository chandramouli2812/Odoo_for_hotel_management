# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class HotelBreakfastItem(models.Model):
    _name = 'hotel.breakfast.item'
    _description = 'Resort Breakfast Menu Item'
    _order = 'category asc, sequence asc, name asc'

    name = fields.Char(string='Item Name', required=True, translate=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(string='Sequence', default=10)
    category = fields.Selection([
        ('bakery', 'Bakery & Breads'),
        ('eggs_hot', 'Eggs & Hot Kitchen'),
        ('indian', 'Indian Specialties'),
        ('healthy_fruits', 'Fruits & Cereals'),
        ('beverages', 'Juices & Hot Beverages'),
        ('specials', 'Chef Specials'),
    ], string='Category', default='bakery', required=True)
    dietary_type = fields.Selection([
        ('veg', 'Vegetarian'),
        ('jain', 'Jain Friendly'),
        ('vegan', 'Vegan'),
        ('egg', 'Contains Egg'),
        ('non_veg', 'Non-Vegetarian'),
    ], string='Dietary Type', default='veg', required=True)
    is_buffet_standard = fields.Boolean(string='Included in Standard Buffet', default=True)
    description = fields.Char(string='Description / Ingredients')
    active = fields.Boolean(string='Active', default=True)

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name


class HotelBreakfastServiceLine(models.Model):
    _name = 'hotel.breakfast.service.line'
    _description = 'Breakfast Service Chosen Item Line'
    _order = 'id asc'

    service_id = fields.Many2one('hotel.breakfast.service', string='Service Attendance', required=True, ondelete='cascade')
    item_id = fields.Many2one('hotel.breakfast.item', string='Breakfast Item', required=True)
    category = fields.Selection(related='item_id.category', string='Category', readonly=True)
    dietary_type = fields.Selection(related='item_id.dietary_type', string='Dietary', readonly=True)
    quantity = fields.Integer(string='Portions', default=1, required=True)
    notes = fields.Char(string='Preparation Note', help='e.g. Well done, Egg white only, Almond milk, Less spicy')


class HotelBreakfastService(models.Model):
    _name = 'hotel.breakfast.service'
    _description = 'Hotel Breakfast & Meal Attendance Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, room_id asc, id desc'

    name = fields.Char(string='Reference', copy=False, readonly=True, default=lambda self: _('New'))
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, index=True, tracking=True)
    reservation_id = fields.Many2one('hotel.reservation', string='Reservation', required=True, ondelete='cascade', tracking=True)
    property_id = fields.Many2one('hotel.property', related='reservation_id.property_id', string='Property', store=True, readonly=True)
    company_id = fields.Many2one('res.company', related='property_id.company_id', string='Company', store=True)

    room_id = fields.Many2one('hotel.room', related='reservation_id.room_id', string='Room', store=True, readonly=True, index=True)
    room_type_id = fields.Many2one('hotel.room.type', related='reservation_id.room_type_id', string='Room Type', store=True, readonly=True)
    guest_id = fields.Many2one('res.partner', related='reservation_id.guest_id', string='Guest Name', store=True, readonly=True)
    guest_phone = fields.Char(related='guest_id.phone', string='Phone', readonly=True)
    
    vip_status = fields.Selection(related='guest_id.vip_status', string='VIP Level', store=True, readonly=True)
    is_vip = fields.Boolean(string='Is VIP Guest', compute='_compute_is_vip', store=True)

    adults = fields.Integer(string='Adults', default=1, tracking=True)
    children = fields.Integer(string='Children', default=0, tracking=True)
    total_covers = fields.Integer(string='Total Covers', compute='_compute_total_covers', store=True)

    meal_plan = fields.Selection([
        ('ep', 'EP - Room Only (Chargeable)'),
        ('cp', 'CP - Bed & Breakfast (Included)'),
        ('map', 'MAP - Half Board (Included)'),
        ('ap', 'AP - Full Board (Included)')
    ], string='Meal Plan', default='cp', required=True, tracking=True)

    breakfast_entitlement = fields.Selection([
        ('included', 'Included (Complimentary)'),
        ('chargeable', 'Chargeable'),
    ], string='Breakfast Status', default='included', required=True, tracking=True)

    service_status = fields.Selection([
        ('pending', 'Pending Service'),
        ('served', 'Served'),
        ('room_service', 'Delivered in Room'),
        ('no_show', 'No-Show / Skipped'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='pending', required=True, tracking=True)

    outlet = fields.Selection([
        ('main_restaurant', 'The Grand Palm (Main Buffet)'),
        ('poolside_cafe', 'Poolside Cafe & Terrace'),
        ('room_service', 'In-Room Dining Tray'),
        ('beach_club', 'Beachfront Lounge')
    ], string='Dining Outlet', default='main_restaurant', tracking=True)

    served_time = fields.Datetime(string='Served Time', tracking=True)
    served_by_id = fields.Many2one('res.users', string='Served By', default=lambda self: self.env.user)
    dietary_notes = fields.Char(string='Dietary / Chef Notes', help="Vegetarian, Jain, Vegan, Food Allergies, Kids meal")
    notes = fields.Text(string='Special Instructions')

    # Choosable Breakfast Items
    item_ids = fields.Many2many('hotel.breakfast.item', string='Choosable Breakfast Items')
    item_line_ids = fields.One2many('hotel.breakfast.service.line', 'service_id', string='Chosen Items & Portions')
    items_summary = fields.Char(string='Chosen Items', compute='_compute_items_summary', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                date_str = vals.get('date') or fields.Date.today().strftime('%Y%m%d')
                if isinstance(date_str, datetime.date):
                    date_str = date_str.strftime('%Y%m%d')
                else:
                    date_str = str(date_str).replace('-', '')
                vals['name'] = f"BRK-{date_str}-{self.env['ir.sequence'].next_by_code('hotel.breakfast.service') or '001'}"
        return super().create(vals_list)

    @api.depends('adults', 'children')
    def _compute_total_covers(self):
        for rec in self:
            rec.total_covers = (rec.adults or 0) + (rec.children or 0)

    @api.depends('vip_status')
    def _compute_is_vip(self):
        for rec in self:
            rec.is_vip = bool(rec.vip_status and rec.vip_status in ('silver', 'gold', 'platinum'))

    @api.depends('item_line_ids.item_id', 'item_line_ids.quantity', 'item_line_ids.notes', 'item_ids')
    def _compute_items_summary(self):
        for rec in self:
            parts = []
            if rec.item_line_ids:
                for line in rec.item_line_ids:
                    qty = f" x{line.quantity}" if line.quantity > 1 else ""
                    note = f" ({line.notes})" if line.notes else ""
                    parts.append(f"{line.item_id.name}{qty}{note}")
            elif rec.item_ids:
                parts = rec.item_ids.mapped('name')
            rec.items_summary = ", ".join(parts) if parts else ""

    @api.onchange('item_ids')
    def _onchange_item_ids(self):
        if self.item_ids:
            existing_ids = self.item_line_ids.mapped('item_id').ids
            new_lines = []
            for item in self.item_ids:
                if item.id not in existing_ids:
                    new_lines.append((0, 0, {
                        'item_id': item.id,
                        'quantity': 1,
                    }))
            if new_lines:
                self.item_line_ids = new_lines

    def action_mark_served(self):
        for rec in self:
            rec.write({
                'service_status': 'served',
                'served_time': fields.Datetime.now(),
                'served_by_id': self.env.uid,
            })

    def action_mark_room_service(self):
        for rec in self:
            rec.write({
                'service_status': 'room_service',
                'outlet': 'room_service',
                'served_time': fields.Datetime.now(),
                'served_by_id': self.env.uid,
            })

    def action_mark_no_show(self):
        for rec in self:
            rec.write({
                'service_status': 'no_show',
            })

    def action_reset(self):
        for rec in self:
            rec.write({
                'service_status': 'pending',
                'served_time': False,
            })

    def get_daily_items_tally(self):
        """Returns aggregated chosen items with total portions for the Chef Prep Board in reports."""
        tally = {}
        for rec in self:
            if rec.item_line_ids:
                for line in rec.item_line_ids:
                    name = line.item_id.name
                    tally[name] = tally.get(name, 0) + (line.quantity or 1)
            elif rec.item_ids:
                for item in rec.item_ids:
                    tally[item.name] = tally.get(item.name, 0) + 1
        return sorted([{'name': k, 'quantity': v} for k, v in tally.items()], key=lambda x: -x['quantity'])

    @api.model
    def action_generate_today_breakfast_list(self, target_date=None):
        """Automatically scans all active reservations and populates the Daily Breakfast Register."""
        if not target_date:
            target_date = fields.Date.context_today(self)
        elif isinstance(target_date, str):
            target_date = fields.Date.from_string(target_date)

        target_datetime_start = datetime.datetime.combine(target_date, datetime.time.min)
        target_datetime_end = datetime.datetime.combine(target_date, datetime.time.max)

        domain = [
            '|',
            ('state', '=', 'check_in'),
            '&', ('state', '=', 'confirmed'), ('check_in', '<=', target_datetime_end),
            ('check_out', '>=', target_datetime_start),
        ]
        reservations = self.env['hotel.reservation'].search(domain)

        created_count = 0
        updated_count = 0

        for res in reservations:
            existing = self.search([
                ('reservation_id', '=', res.id),
                ('date', '=', target_date),
            ], limit=1)

            entitlement = 'included' if res.meal_plan in ('cp', 'map', 'ap') else 'chargeable'
            dietary = res.dietary_notes or (res.guest_id.guest_notes if res.guest_id else False) or ''

            vals = {
                'reservation_id': res.id,
                'date': target_date,
                'adults': res.adults or 1,
                'children': res.children or 0,
                'meal_plan': res.meal_plan or 'cp',
                'breakfast_entitlement': entitlement,
                'dietary_notes': dietary,
            }

            if hasattr(res, 'breakfast_item_ids') and res.breakfast_item_ids:
                vals['item_ids'] = [(6, 0, res.breakfast_item_ids.ids)]

            if existing:
                existing.write({
                    'adults': vals['adults'],
                    'children': vals['children'],
                    'meal_plan': vals['meal_plan'],
                    'breakfast_entitlement': vals['breakfast_entitlement'],
                    'dietary_notes': vals['dietary_notes'],
                })
                if hasattr(res, 'breakfast_item_ids') and res.breakfast_item_ids and not existing.item_ids:
                    existing.write({'item_ids': [(6, 0, res.breakfast_item_ids.ids)]})
                    existing._onchange_item_ids()
                updated_count += 1
            else:
                new_rec = self.create(vals)
                if new_rec.item_ids and not new_rec.item_line_ids:
                    new_rec._onchange_item_ids()
                created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Breakfast List Synced!"),
                'message': _("Successfully prepared breakfast list for %s: %d new added, %d updated.") % (
                    target_date, created_count, updated_count
                ),
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.client', 'tag': 'reload'}
            }
        }
