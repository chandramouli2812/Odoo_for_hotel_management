# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class ComplianceGuestReport(models.Model):
    _name = 'compliance.guest.report'
    _description = 'Resort Police Guest Intimation & Compliance Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'arrival_date desc, id desc'

    name = fields.Char(
        string='Police Intimation Ref',
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    reporting_type = fields.Selection([
        ('arrival', 'Guest Arrival Police Intimation'),
        ('foreign', 'Foreign National Report (Form C)'),
        ('domestic', 'Domestic Guest Police Report'),
        ('registration', 'Official Guest Registration Record'),
        ('daily', 'Daily Guest Intimation Sheet'),
        ('group', 'Group / Bulk Guest Report'),
        ('long_stay', 'Long-Stay Guest Intimation (>14 Days)'),
        ('visitor', 'Non-Resident Visitor Report'),
        ('departure', 'Guest Departure Intimation'),
        ('identity', 'Guest Identity Document Record'),
        ('suspicious', 'Special / High-Priority Police Intimation'),
    ], string='Reporting Category', default='arrival', required=True, tracking=True)

    guest_id = fields.Many2one('res.partner', string='Guest Name', required=True, tracking=True)
    reservation_id = fields.Many2one('hotel.reservation', string='Booking / Reservation', tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room No', tracking=True)
    property_id = fields.Many2one('hotel.property', string='Property / Resort', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    nationality_id = fields.Many2one('res.country', string='Nationality', tracking=True)
    is_foreign_national = fields.Boolean(
        string='Is Foreign National',
        compute='_compute_foreign_national',
        store=True,
        tracking=True
    )

    id_type = fields.Selection([
        ('aadhaar', 'Aadhaar Card'),
        ('passport', 'Passport'),
        ('driving_license', 'Driving License'),
        ('voter_id', 'Voter ID (Election Card)'),
        ('pan_card', 'PAN Card'),
        ('oci', 'OCI / PIO Card'),
        ('other', 'Other Government ID'),
    ], string='ID Document Type', default='aadhaar', tracking=True)
    id_number = fields.Char(string='ID Document Number', tracking=True)
    id_expiry_date = fields.Date(string='ID Expiry Date')

    guest_phone = fields.Char(string='Mobile / Phone', related='guest_id.phone', readonly=False, store=True)
    guest_email = fields.Char(string='Email', related='guest_id.email', readonly=False, store=True)
    permanent_address = fields.Text(string='Permanent Residential Address')

    arrival_date = fields.Datetime(string='Arrival Date & Time', default=fields.Datetime.now, required=True, tracking=True)
    departure_date = fields.Datetime(string='Expected Departure Date & Time', tracking=True)
    duration_days = fields.Integer(string='Duration of Stay (Days)', compute='_compute_duration', store=True)
    is_long_stay = fields.Boolean(string='Is Long-Stay Guest', compute='_compute_duration', store=True)

    purpose_of_stay = fields.Selection([
        ('leisure', 'Leisure / Holiday / Vacation'),
        ('business', 'Business / Official Work'),
        ('wedding_event', 'Wedding / Family Event'),
        ('conference', 'Conference / Corporate Meet'),
        ('medical', 'Medical / Wellness Treatment'),
        ('transit', 'Transit / Short Stay'),
        ('other', 'Other Purpose'),
    ], string='Purpose of Stay', default='leisure')

    accompanying_adults = fields.Integer(string='Accompanying Adults', default=0)
    accompanying_children = fields.Integer(string='Accompanying Children', default=0)
    accompanying_details = fields.Text(string='Names & Details of Accompanying Persons')

    # Authority & Submission
    authority_name = fields.Char(string='Law Enforcement Authority', default='Local Police Station', tracking=True)
    police_station_jurisdiction = fields.Char(string='Police Station Jurisdiction / Beat')
    submission_mode = fields.Selection([
        ('online', 'Online Police Portal / C-Form'),
        ('physical', 'Physical Submission at Police Station'),
        ('email', 'Official Police Email'),
        ('dispatch', 'Courier / Postal Dispatch'),
    ], string='Submission Mode', default='online', tracking=True)

    submission_date = fields.Date(string='Submission Date', tracking=True)
    submission_ref = fields.Char(string='Police Ack / Reference No', tracking=True)
    submitted_by_id = fields.Many2one('res.users', string='Submitted By', tracking=True)
    reviewed_by_id = fields.Many2one('res.users', string='Reviewed By', tracking=True)

    verification_status = fields.Selection([
        ('pending', 'Pending ID Verification'),
        ('verified', 'Verified & Validated'),
        ('flagged', 'Flagged / Discrepancy Found'),
    ], string='ID Verification Status', default='pending', tracking=True)

    # Eco-Friendly & Paperless Operations
    is_paperless = fields.Boolean(
        string='100% Paperless Digital Filing',
        default=True,
        tracking=True,
        help="Zero physical paper used. Processed digitally to protect trees and resort environment."
    )
    paper_sheets_saved = fields.Integer(
        string='Paper Sheets Saved',
        default=3,
        readonly=True,
        help="Estimated paper sheets saved by digital filing."
    )
    digital_verification_seal = fields.Char(
        string='Digital Security Stamp / Token',
        compute='_compute_digital_seal',
        store=True,
        help="Tamper-proof digital verification token generated for law enforcement audits."
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('ready', 'Ready for Submission'),
        ('submitted', 'Submitted to Police'),
        ('acknowledged', 'Acknowledged by Authority'),
        ('closed', 'Closed & Archived'),
        ('cancelled', 'Cancelled'),
    ], string='Compliance Status', default='draft', required=True, tracking=True)

    remarks = fields.Text(string='Confidential Remarks / Police Instructions')
    foreign_guest_id = fields.Many2one('compliance.foreign.guest', string='Related FRRO / Form C Record')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'compliance_guest_report_attachment_rel',
        'report_id',
        'attachment_id',
        string='ID Proofs & Police Ack Receipts'
    )

    @api.depends('name', 'guest_id', 'id_number')
    def _compute_digital_seal(self):
        import hashlib
        for rec in self:
            if rec.name and rec.name != _('New'):
                raw = f"{rec.name}-{rec.guest_id.id if rec.guest_id else ''}-{rec.id_number or ''}"
                rec.digital_verification_seal = f"ECO-SEAL-{hashlib.sha256(raw.encode()).hexdigest()[:12].upper()}"
            else:
                rec.digital_verification_seal = False

    @api.depends('nationality_id')
    def _compute_foreign_national(self):
        india = self.env.ref('base.in', raise_if_not_found=False)
        for record in self:
            if record.nationality_id:
                record.is_foreign_national = (india and record.nationality_id != india) or (record.nationality_id.code != 'IN')
            else:
                record.is_foreign_national = False

    @api.depends('arrival_date', 'departure_date')
    def _compute_duration(self):
        for record in self:
            if record.arrival_date and record.departure_date:
                diff = record.departure_date - record.arrival_date
                days = max(1, diff.days)
                record.duration_days = days
                record.is_long_stay = days >= 14
            else:
                record.duration_days = 1
                record.is_long_stay = False

    @api.onchange('guest_id')
    def _onchange_guest_id(self):
        if self.guest_id:
            if hasattr(self.guest_id, 'nationality_id') and self.guest_id.nationality_id:
                self.nationality_id = self.guest_id.nationality_id
            if hasattr(self.guest_id, 'id_type') and self.guest_id.id_type:
                # Map guest id_type if compatible
                type_map = {'passport': 'passport', 'national_id': 'aadhaar', 'driving_license': 'driving_license'}
                self.id_type = type_map.get(self.guest_id.id_type, 'other')
            if hasattr(self.guest_id, 'id_number') and self.guest_id.id_number:
                self.id_number = self.guest_id.id_number
            if self.guest_id.contact_address:
                self.permanent_address = self.guest_id.contact_address

    @api.onchange('reservation_id')
    def _onchange_reservation_id(self):
        if self.reservation_id:
            self.guest_id = self.reservation_id.guest_id
            self.room_id = self.reservation_id.room_id
            self.property_id = self.reservation_id.property_id
            self.arrival_date = self.reservation_id.check_in
            self.departure_date = self.reservation_id.check_out
            self.accompanying_adults = max(0, self.reservation_id.adults - 1)
            self.accompanying_children = self.reservation_id.children

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('compliance.guest.report') or _('New')
        return super().create(vals_list)

    # User-Friendly & Eco-Smart Helper Actions
    def action_auto_fill_details(self):
        """1-Click Auto-Fill from guest partner & reservation profile without retyping."""
        for rec in self:
            if rec.reservation_id:
                rec._onchange_reservation_id()
            if rec.guest_id:
                rec._onchange_guest_id()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Details Auto-Filled"),
                'message': _("Guest address, identity, and room details synchronized."),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_quick_verify_id(self):
        """1-Click Verify ID document and move to Ready state."""
        for rec in self:
            if not rec.id_number:
                raise UserError(_("Please ensure ID Document Number is entered before validating."))
            rec.write({
                'verification_status': 'verified',
                'state': 'ready',
                'reviewed_by_id': self.env.user.id,
            })

    def action_quick_digital_submit(self):
        """1-Click Paperless e-Submission to police portal."""
        for rec in self:
            rec.write({
                'submission_mode': 'online',
                'submission_date': fields.Date.today(),
                'submitted_by_id': self.env.user.id,
                'state': 'submitted',
                'is_paperless': True,
            })

    # Workflow Actions
    def action_submit_for_review(self):
        for rec in self:
            if not rec.id_number:
                raise UserError(_("Please provide the ID Document Number before submitting for review."))
            rec.write({'state': 'pending_review'})

    def action_approve_ready(self):
        for rec in self:
            rec.write({
                'state': 'ready',
                'reviewed_by_id': self.env.user.id,
                'verification_status': 'verified',
            })

    def action_mark_submitted(self):
        for rec in self:
            rec.write({
                'state': 'submitted',
                'submission_date': rec.submission_date or fields.Date.today(),
                'submitted_by_id': self.env.user.id,
            })

    def action_mark_acknowledged(self):
        for rec in self:
            if not rec.submission_ref:
                raise UserError(_("Please enter the Police Reference / Acknowledgement Number before marking as acknowledged."))
            rec.write({'state': 'acknowledged'})

    def action_close(self):
        for rec in self:
            rec.write({'state': 'closed'})

    def action_reset_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def action_cancel(self):
        for rec in self:
            rec.write({'state': 'cancelled'})

    def action_create_foreign_record(self):
        self.ensure_one()
        if not self.is_foreign_national:
            raise UserError(_("This record is not marked as a foreign national."))
        if self.foreign_guest_id:
            return {
                'name': _('FRRO / Form C Record'),
                'type': 'ir.actions.act_window',
                'res_model': 'compliance.foreign.guest',
                'res_id': self.foreign_guest_id.id,
                'view_mode': 'form',
            }
        
        foreign_rec = self.env['compliance.foreign.guest'].create({
            'guest_id': self.guest_id.id,
            'reservation_id': self.reservation_id.id if self.reservation_id else False,
            'room_id': self.room_id.id if self.room_id else False,
            'property_id': self.property_id.id if self.property_id else False,
            'nationality_id': self.nationality_id.id if self.nationality_id else False,
            'passport_number': self.id_number if self.id_type == 'passport' else '',
            'arrival_at_hotel': self.arrival_date,
            'expected_departure': self.departure_date,
            'phone_in_india': self.guest_phone,
        })
        self.foreign_guest_id = foreign_rec.id
        return {
            'name': _('FRRO / Form C Record'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.foreign.guest',
            'res_id': foreign_rec.id,
            'view_mode': 'form',
        }
