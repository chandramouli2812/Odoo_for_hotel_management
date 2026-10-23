# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date, timedelta

class HotelDailyFlashReport(models.TransientModel):
    _name = 'hotel.daily.flash.report'
    _description = 'Executive Daily Resort Flash Report'

    report_date = fields.Date(string='Report Date', default=fields.Date.context_today, required=True)
    property_id = fields.Many2one('hotel.property', string='Property / Resort')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    # Occupancy & Room KPIs
    total_rooms = fields.Integer(string='Total Rooms', compute='_compute_metrics')
    available_rooms = fields.Integer(string='Available Rooms', compute='_compute_metrics')
    occupied_rooms = fields.Integer(string='Occupied Rooms', compute='_compute_metrics')
    vacant_rooms = fields.Integer(string='Vacant Rooms', compute='_compute_metrics')
    blocked_rooms = fields.Integer(string='Out of Order / Blocked', compute='_compute_metrics')
    occupancy_rate = fields.Float(string='Occupancy (%)', compute='_compute_metrics')
    adr = fields.Monetary(string='ADR (Average Daily Rate)', compute='_compute_metrics', currency_field='currency_id')
    revpar = fields.Monetary(string='RevPAR (Rev per Avail Room)', compute='_compute_metrics', currency_field='currency_id')
    revpor = fields.Monetary(string='RevPOR (Rev per Occ Room)', compute='_compute_metrics', currency_field='currency_id')
    alos = fields.Float(string='ALOS (Avg Length of Stay)', compute='_compute_metrics')

    # Guest Movement
    expected_arrivals = fields.Integer(string='Expected Arrivals', compute='_compute_metrics')
    checked_in_arrivals = fields.Integer(string='Actual Check-Ins Today', compute='_compute_metrics')
    stayover_count = fields.Integer(string='Stayovers In-House', compute='_compute_metrics')
    expected_departures = fields.Integer(string='Expected Departures', compute='_compute_metrics')
    checked_out_departures = fields.Integer(string='Actual Check-Outs Today', compute='_compute_metrics')
    in_house_guests = fields.Integer(string='In-House Guests', compute='_compute_metrics')
    vip_count = fields.Integer(string='VIP Guests In-House', compute='_compute_metrics')
    no_show_count = fields.Integer(string='No-Shows Today', compute='_compute_metrics')
    cancellation_count = fields.Integer(string='Cancellations Today', compute='_compute_metrics')

    # Departmental Revenue Breakdown
    room_revenue = fields.Monetary(string='Room Accommodation Revenue', compute='_compute_metrics', currency_field='currency_id')
    restaurant_revenue = fields.Monetary(string='Restaurant & F&B Revenue', compute='_compute_metrics', currency_field='currency_id')
    bar_revenue = fields.Monetary(string='Bar & Beverage Revenue', compute='_compute_metrics', currency_field='currency_id')
    spa_revenue = fields.Monetary(string='Spa & Wellness Revenue', compute='_compute_metrics', currency_field='currency_id')
    activity_revenue = fields.Monetary(string='Activities & Recreation Revenue', compute='_compute_metrics', currency_field='currency_id')
    laundry_revenue = fields.Monetary(string='Laundry Revenue', compute='_compute_metrics', currency_field='currency_id')
    other_revenue = fields.Monetary(string='Other Ancillary Revenue', compute='_compute_metrics', currency_field='currency_id')
    total_resort_revenue = fields.Monetary(string='Total Gross Resort Revenue', compute='_compute_metrics', currency_field='currency_id')

    # Cashier Collections & Balances
    cash_collected = fields.Monetary(string='Cash Collection', compute='_compute_metrics', currency_field='currency_id')
    card_collected = fields.Monetary(string='Card Collection', compute='_compute_metrics', currency_field='currency_id')
    upi_collected = fields.Monetary(string='UPI / QR / Digital', compute='_compute_metrics', currency_field='currency_id')
    bank_collected = fields.Monetary(string='Bank Transfer', compute='_compute_metrics', currency_field='currency_id')
    discounts_given = fields.Monetary(string='Discounts & Allowances', compute='_compute_metrics', currency_field='currency_id')
    refunds_issued = fields.Monetary(string='Refunds & Adjustments', compute='_compute_metrics', currency_field='currency_id')
    total_collected = fields.Monetary(string='Total Collections Today', compute='_compute_metrics', currency_field='currency_id')
    total_outstanding_due = fields.Monetary(string='Total Outstanding Guest Balances', compute='_compute_metrics', currency_field='currency_id')

    # Housekeeping & Resort Maintenance Condition
    clean_rooms = fields.Integer(string='Clean & Ready', compute='_compute_metrics')
    inspected_rooms = fields.Integer(string='Inspected & Approved', compute='_compute_metrics')
    dirty_rooms = fields.Integer(string='Dirty / Needs Cleaning', compute='_compute_metrics')
    cleaning_rooms = fields.Integer(string='Cleaning In Progress', compute='_compute_metrics')
    maintenance_open_issues = fields.Integer(string='Open Maintenance Issues', compute='_compute_metrics')
    maintenance_urgent_issues = fields.Integer(string='Urgent / High Priority Repairs', compute='_compute_metrics')

    @api.depends('report_date', 'property_id')
    def _compute_metrics(self):
        for rec in self:
            r_date = rec.report_date or fields.Date.context_today(rec)
            start_dt = datetime.combine(r_date, datetime.min.time())
            end_dt = datetime.combine(r_date, datetime.max.time())

            # 1. Rooms Domain
            room_domain = [('active', '=', True)]
            if rec.property_id:
                room_domain.append(('property_id', '=', rec.property_id.id))
            all_rooms = self.env['hotel.room'].search(room_domain)
            total_r = len(all_rooms)
            rec.total_rooms = total_r

            blocked_r = len(all_rooms.filtered(lambda rm: rm.maintenance_status in ('maintenance', 'out_of_service')))
            rec.blocked_rooms = blocked_r
            rec.available_rooms = max(0, total_r - blocked_r)

            rec.clean_rooms = len(all_rooms.filtered(lambda rm: rm.housekeeping_status == 'clean'))
            rec.inspected_rooms = len(all_rooms.filtered(lambda rm: rm.housekeeping_status == 'inspected'))
            rec.dirty_rooms = len(all_rooms.filtered(lambda rm: rm.housekeeping_status == 'dirty'))
            rec.cleaning_rooms = len(all_rooms.filtered(lambda rm: rm.housekeeping_status == 'cleaning'))

            # 2. Reservations Overlapping the Report Date
            res_domain = [
                ('state', 'in', ('confirmed', 'check_in', 'check_out')),
                ('check_in', '<=', end_dt),
                ('check_out', '>=', start_dt),
            ]
            if rec.property_id:
                res_domain.append(('property_id', '=', rec.property_id.id))
            active_res = self.env['hotel.reservation'].search(res_domain)

            # In-House & Occupied
            in_house_res = active_res.filtered(lambda r: r.state == 'check_in' or (r.check_in <= end_dt and r.check_out > start_dt and r.state in ('confirmed', 'check_in')))
            occupied_count = len(in_house_res)
            rec.occupied_rooms = occupied_count
            rec.vacant_rooms = max(0, total_r - occupied_count - blocked_r)

            # Occupancy Rate
            rec.occupancy_rate = (occupied_count / total_r * 100.0) if total_r > 0 else 0.0

            # Room Revenue & ADR / RevPAR / ALOS
            room_rev = sum(r.rate_per_night for r in in_house_res)
            rec.room_revenue = room_rev
            rec.adr = (room_rev / occupied_count) if occupied_count > 0 else 0.0
            rec.revpar = (room_rev / total_r) if total_r > 0 else 0.0
            rec.alos = (sum(r.nights for r in in_house_res) / float(occupied_count)) if occupied_count > 0 else 0.0

            # Arrivals, Departures & Stayovers
            arr_domain = [
                ('check_in', '>=', start_dt),
                ('check_in', '<=', end_dt),
                ('state', 'in', ('confirmed', 'check_in')),
            ]
            if rec.property_id:
                arr_domain.append(('property_id', '=', rec.property_id.id))
            today_arr = self.env['hotel.reservation'].search(arr_domain)
            rec.expected_arrivals = len(today_arr)
            rec.checked_in_arrivals = len(today_arr.filtered(lambda r: r.state == 'check_in'))

            dep_domain = [
                ('check_out', '>=', start_dt),
                ('check_out', '<=', end_dt),
                ('state', 'in', ('check_in', 'check_out')),
            ]
            if rec.property_id:
                dep_domain.append(('property_id', '=', rec.property_id.id))
            today_dep = self.env['hotel.reservation'].search(dep_domain)
            rec.expected_departures = len(today_dep)
            rec.checked_out_departures = len(today_dep.filtered(lambda r: r.state == 'check_out'))

            # Stayovers (checked in before today and checking out after today)
            stayovers = in_house_res.filtered(lambda r: r.check_in < start_dt and r.check_out > end_dt)
            rec.stayover_count = len(stayovers)

            # No-Shows (confirmed arrivals scheduled on or before report date not yet checked in)
            no_show_res = today_arr.filtered(lambda r: r.state == 'confirmed')
            rec.no_show_count = len(no_show_res)

            # Cancellations on report date
            cancel_domain = [
                ('state', '=', 'cancel'),
                ('write_date', '>=', start_dt),
                ('write_date', '<=', end_dt),
            ]
            if rec.property_id:
                cancel_domain.append(('property_id', '=', rec.property_id.id))
            rec.cancellation_count = self.env['hotel.reservation'].search_count(cancel_domain)

            # In-House Guest count & VIPs
            rec.in_house_guests = sum(r.adults + r.children for r in in_house_res)
            rec.vip_count = len(in_house_res.filtered(lambda r: r.guest_id.vip_status and r.guest_id.vip_status not in ('standard', False)))

            # 3. Departmental Revenues from Folios & Lines
            folio_domain = [
                ('create_date', '>=', start_dt),
                ('create_date', '<=', end_dt),
            ]
            if rec.property_id:
                folio_domain.append(('property_id', '=', rec.property_id.id))
            lines = self.env['hotel.folio.line'].search([
                ('folio_id.create_date', '>=', start_dt),
                ('folio_id.create_date', '<=', end_dt),
            ])
            if rec.property_id:
                lines = lines.filtered(lambda l: l.folio_id.property_id.id == rec.property_id.id)

            restaurant_rev = sum(l.price_subtotal for l in lines.filtered(lambda l: l.service_type == 'restaurant'))
            bar_rev = sum(l.price_subtotal for l in lines.filtered(lambda l: l.service_type in ('bar', 'minibar')))
            spa_rev = sum(l.price_subtotal for l in lines.filtered(lambda l: l.service_type == 'spa'))
            activity_rev = sum(l.price_subtotal for l in lines.filtered(lambda l: l.service_type == 'activity'))
            laundry_rev = sum(l.price_subtotal for l in lines.filtered(lambda l: l.service_type == 'laundry'))
            other_rev = sum(l.price_subtotal for l in lines.filtered(lambda l: l.service_type == 'other'))

            # Add POS Orders if POS installed
            pos_orders = self.env['pos.order'].search([
                ('date_order', '>=', start_dt),
                ('date_order', '<=', end_dt),
                ('state', 'in', ('paid', 'done', 'invoiced'))
            ])
            if pos_orders:
                restaurant_rev += sum(pos_orders.mapped('amount_total'))

            rec.restaurant_revenue = restaurant_rev
            rec.bar_revenue = bar_rev
            rec.spa_revenue = spa_rev
            rec.activity_revenue = activity_rev
            rec.laundry_revenue = laundry_rev
            rec.other_revenue = other_rev
            rec.total_resort_revenue = room_rev + restaurant_rev + bar_rev + spa_rev + activity_rev + laundry_rev + other_rev
            rec.revpor = (rec.total_resort_revenue / occupied_count) if occupied_count > 0 else 0.0

            # 4. Collections Today (from Hotel Folio Payments)
            pay_domain = [
                ('payment_date', '>=', start_dt),
                ('payment_date', '<=', end_dt),
            ]
            if rec.property_id:
                pay_domain.append(('folio_id.property_id', '=', rec.property_id.id))
            payments = self.env['hotel.folio.payment'].search(pay_domain)

            rec.cash_collected = sum(p.amount for p in payments.filtered(lambda p: p.payment_method == 'cash'))
            rec.card_collected = sum(p.amount for p in payments.filtered(lambda p: p.payment_method == 'card'))
            rec.upi_collected = sum(p.amount for p in payments.filtered(lambda p: p.payment_method == 'upi'))
            rec.bank_collected = sum(p.amount for p in payments.filtered(lambda p: p.payment_method == 'bank'))
            rec.discounts_given = sum(abs(l.price_subtotal) for l in lines if l.price_subtotal < 0)
            rec.refunds_issued = sum(abs(p.amount) for p in payments if p.amount < 0)
            rec.total_collected = rec.cash_collected + rec.card_collected + rec.upi_collected + rec.bank_collected

            # Total Outstanding Due (Across all active folios)
            all_active_folios = self.env['hotel.folio'].search([('state', '!=', 'cancel')])
            if rec.property_id:
                all_active_folios = all_active_folios.filtered(lambda f: f.property_id.id == rec.property_id.id)
            rec.total_outstanding_due = sum(all_active_folios.mapped('amount_due'))

            # 5. Maintenance Requests
            if 'maintenance.request' in self.env:
                maint_domain = [('state', 'not in', ('done', 'cancelled'))]
                rec.maintenance_open_issues = self.env['maintenance.request'].search_count(maint_domain)
                rec.maintenance_urgent_issues = self.env['maintenance.request'].search_count(maint_domain + [('priority', 'in', ('2', '3'))])
            else:
                rec.maintenance_open_issues = blocked_r
                rec.maintenance_urgent_issues = 0

    @api.model
    def action_open_dashboard(self):
        """Action for top menu: opens today's flash report immediately with calculated metrics."""
        today = fields.Date.context_today(self)
        report = self.search([('report_date', '=', today)], order='id desc', limit=1)
        if not report:
            report = self.create({'report_date': today})
        else:
            report._compute_metrics()

        return {
            'name': _('Executive Daily Resort Flash Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.daily.flash.report',
            'res_id': report.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_set_today(self):
        """Switch report to today with 1-click"""
        self.report_date = fields.Date.context_today(self)
        self._compute_metrics()
        return self.action_refresh()

    def action_set_yesterday(self):
        """Switch report to yesterday with 1-click"""
        self.report_date = fields.Date.context_today(self) - timedelta(days=1)
        self._compute_metrics()
        return self.action_refresh()

    def action_refresh(self):
        """Recompute live metrics on demand"""
        self._compute_metrics()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.daily.flash.report',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_print_pdf(self):
        """Generate and print the Executive Daily Resort Flash Report PDF"""
        self.ensure_one()
        return self.env.ref('mouli_hotels.action_report_daily_flash').report_action(self)

    def action_view_arrivals(self):
        """Drill-down: View reservations checking in on the report date"""
        self.ensure_one()
        r_date = self.report_date or fields.Date.context_today(self)
        domain = [
            ('check_in', '>=', datetime.combine(r_date, datetime.min.time())),
            ('check_in', '<=', datetime.combine(r_date, datetime.max.time())),
            ('state', 'in', ['confirmed', 'check_in'])
        ]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Arrivals - %s") % r_date,
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_departures(self):
        """Drill-down: View reservations checking out on the report date"""
        self.ensure_one()
        r_date = self.report_date or fields.Date.context_today(self)
        domain = [
            ('check_out', '>=', datetime.combine(r_date, datetime.min.time())),
            ('check_out', '<=', datetime.combine(r_date, datetime.max.time())),
            ('state', 'in', ['check_in', 'check_out'])
        ]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Departures - %s") % r_date,
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_in_house(self):
        """Drill-down: View currently checked-in guests"""
        self.ensure_one()
        domain = [('state', '=', 'check_in')]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Current In-House Guests"),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_vip_guests(self):
        """Drill-down: View in-house VIP guests"""
        self.ensure_one()
        domain = [
            ('state', '=', 'check_in'),
            ('guest_id.vip_status', 'in', ['silver', 'gold', 'platinum', 'diamond'])
        ]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("In-House VIP Guests"),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_occupied_rooms(self):
        """Drill-down: View occupied rooms"""
        self.ensure_one()
        domain = [('occupancy_status', '=', 'occupied')]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Occupied Rooms"),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.room',
            'view_mode': 'kanban,list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_vacant_rooms(self):
        """Drill-down: View vacant ready rooms"""
        self.ensure_one()
        domain = [('occupancy_status', '=', 'vacant')]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Vacant Available Rooms"),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.room',
            'view_mode': 'kanban,list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_dirty_rooms(self):
        """Drill-down: View dirty rooms needing turnaround or cleaning"""
        self.ensure_one()
        domain = [('housekeeping_status', '=', 'dirty')]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Dirty Rooms (Housekeeping Turnaround)"),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.room',
            'view_mode': 'kanban,list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_guest_ledger(self):
        """Drill-down: View guest folios with outstanding balances"""
        self.ensure_one()
        domain = [('amount_due', '>', 0), ('state', '!=', 'cancel')]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Guest Ledger - Outstanding Balances"),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.folio',
            'view_mode': 'list,pivot,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_fnb_orders(self):
        """Drill-down: View restaurant POS orders"""
        self.ensure_one()
        r_date = self.report_date or fields.Date.context_today(self)
        domain = [
            ('date_order', '>=', datetime.combine(r_date, datetime.min.time())),
            ('date_order', '<=', datetime.combine(r_date, datetime.max.time())),
            ('state', 'in', ('paid', 'done', 'invoiced'))
        ]
        return {
            'name': _("Restaurant & F&B Orders - %s") % r_date,
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'list,pivot,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_stayovers(self):
        """Drill-down: View stayover reservations"""
        self.ensure_one()
        r_date = self.report_date or fields.Date.context_today(self)
        start_dt = datetime.combine(r_date, datetime.min.time())
        end_dt = datetime.combine(r_date, datetime.max.time())
        domain = [
            ('check_in', '<', start_dt),
            ('check_out', '>', end_dt),
            ('state', 'in', ('confirmed', 'check_in'))
        ]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Stayover Guests - %s") % r_date,
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_no_shows(self):
        """Drill-down: View confirmed reservations that did not check in"""
        self.ensure_one()
        r_date = self.report_date or fields.Date.context_today(self)
        start_dt = datetime.combine(r_date, datetime.min.time())
        end_dt = datetime.combine(r_date, datetime.max.time())
        domain = [
            ('check_in', '>=', start_dt),
            ('check_in', '<=', end_dt),
            ('state', '=', 'confirmed')
        ]
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
        return {
            'name': _("Expected / Unclaimed Arrivals - %s") % r_date,
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_view_maintenance(self):
        """Drill-down: View open maintenance requests"""
        self.ensure_one()
        domain = [('state', 'not in', ('done', 'cancelled'))]
        return {
            'name': _("Active Resort Maintenance Issues"),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'kanban,list,form',
            'domain': domain,
            'target': 'current',
        }

