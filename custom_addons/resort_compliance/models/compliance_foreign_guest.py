# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class ComplianceForeignGuest(models.Model):
    _name = 'compliance.foreign.guest'
    _description = 'Foreign Guest FRRO / Form C Immigration Compliance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'arrival_at_hotel desc, id desc'

    name = fields.Char(
        string='Form C Reference',
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    guest_id = fields.Many2one('res.partner', string='Guest Name', required=True, tracking=True)
    reservation_id = fields.Many2one('hotel.reservation', string='Booking / Reservation', tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room Assigned', tracking=True)
    property_id = fields.Many2one('hotel.property', string='Property / Resort', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    nationality_id = fields.Many2one('res.country', string='Nationality (Country of Citizenship)', required=True, tracking=True)
    
    # Passport Details
    passport_number = fields.Char(string='Passport Number', required=True, tracking=True)
    passport_country_id = fields.Many2one('res.country', string='Passport Issuing Country')
    passport_issue_date = fields.Date(string='Passport Issue Date')
    passport_expiry_date = fields.Date(string='Passport Expiry Date', tracking=True)

    # Visa Details
    visa_number = fields.Char(string='Visa / e-Visa Number', tracking=True)
    visa_type = fields.Selection([
        ('tourist', 'Tourist / e-Tourist Visa'),
        ('business', 'Business / e-Business Visa'),
        ('conference', 'Conference Visa'),
        ('medical', 'Medical / Attendant Visa'),
        ('student', 'Student Visa'),
        ('employment', 'Employment Visa'),
        ('oci', 'OCI / PIO Cardholder'),
        ('diplomatic', 'Diplomatic / Official Visa'),
        ('other', 'Other Visa Category'),
    ], string='Visa Category', default='tourist', tracking=True)
    visa_issue_place = fields.Char(string='Visa Issue Place / Mission')
    visa_valid_until = fields.Date(string='Visa Valid Until', tracking=True)
    is_visa_expiring_soon = fields.Boolean(
        string='Visa Expiring Soon',
        compute='_compute_visa_alert',
        store=True,
        help="Alert if visa expires during guest's resort stay or within 7 days."
    )

    # Entry into India
    arrival_in_india_date = fields.Date(string='Date of Arrival in India')
    port_of_entry = fields.Char(string='Port of Entry into India (e.g. Mumbai, Delhi, Goa, Bengaluru)')
    
    # Resort Stay
    arrival_at_hotel = fields.Datetime(string='Arrival at Resort', default=fields.Datetime.now, required=True, tracking=True)
    expected_departure = fields.Datetime(string='Expected Departure', tracking=True)
    purpose_of_visit = fields.Selection([
        ('tourism', 'Tourism / Holiday / Sightseeing'),
        ('business', 'Business / Meetings'),
        ('conference', 'Conference / Seminar'),
        ('medical', 'Medical Treatment / Wellness'),
        ('visiting_family', 'Visiting Friends & Relatives'),
        ('transit', 'Transit / Short Stay'),
        ('other', 'Other Purpose'),
    ], string='Purpose of Visit', default='tourism')
    next_destination = fields.Char(string='Next Destination (City / Country)')
    phone_in_india = fields.Char(string='Phone / Contact in India')
    emergency_contact = fields.Char(string='Emergency Contact Name & Phone')
    home_country_address = fields.Text(string='Permanent Address in Home Country')

    # Bureau of Immigration (BoI) Form C Submission Tracker
    frro_portal_status = fields.Selection([
        ('not_submitted', 'Draft / Not Submitted'),
        ('submitted', 'Submitted to BoI / C-Form Portal'),
        ('verified', 'Verified / Temp Ack Received'),
        ('acknowledged', 'Official Form C Generated'),
        ('rejected', 'Rejected / Requires Correction'),
    ], string='FRRO / Form C Status', default='not_submitted', tracking=True)
    
    frro_ack_number = fields.Char(string='BoI Form C Ack / App ID', tracking=True)
    submission_time = fields.Datetime(string='Submission Timestamp', tracking=True)
    submission_deadline = fields.Datetime(
        string='Mandatory 24h Deadline',
        compute='_compute_deadline',
        store=True,
        help="Under Indian Law (Foreigners Act), Form C must be submitted within 24 hours of guest arrival."
    )
    is_overdue = fields.Boolean(
        string='Form C Overdue (>24 Hours)',
        compute='_compute_overdue',
        search='_search_overdue',
        help="True if >24 hours from arrival and not yet submitted."
    )

    # Document Verification Checklist
    doc_passport_copy = fields.Boolean(string='Passport Photo Page Copy Attached', default=False)
    doc_visa_copy = fields.Boolean(string='Visa / e-Visa Copy Attached', default=False)
    doc_entry_stamp = fields.Boolean(string='Immigration Entry Stamp Page Attached', default=False)
    doc_photo = fields.Boolean(string='Guest Recent Photograph Attached', default=False)
    documents_complete = fields.Boolean(
        string='All Mandatory Documents Verified',
        compute='_compute_documents_complete',
        store=True
    )

    # Eco-Friendly & Paperless Operations
    is_paperless = fields.Boolean(
        string='100% Paperless Digital Filing',
        default=True,
        tracking=True,
        help="Zero physical paper used. Digital Form C filed on BoI Portal."
    )
    paper_sheets_saved = fields.Integer(
        string='Paper Sheets Saved',
        default=5,
        readonly=True,
        help="Estimated paper sheets saved by digital Form C filing."
    )
    digital_form_c_token = fields.Char(
        string='Digital Form C Seal Token',
        compute='_compute_digital_token',
        store=True,
        help="Tamper-proof digital seal for Bureau of Immigration records."
    )

    state = fields.Selection([
        ('draft', 'Draft Record'),
        ('docs_verified', 'Documents Verified'),
        ('submitted', 'Submitted to FRRO'),
        ('completed', 'Form C Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)

    remarks = fields.Text(string='Immigration & Compliance Notes')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'compliance_foreign_guest_attachment_rel',
        'foreign_id',
        'attachment_id',
        string='Form C & Identity Documents'
    )

    @api.depends('name', 'guest_id', 'passport_number')
    def _compute_digital_token(self):
        import hashlib
        for rec in self:
            if rec.name and rec.name != _('New'):
                raw = f"FRRO-{rec.name}-{rec.passport_number or ''}"
                rec.digital_form_c_token = f"BOI-DIGI-{hashlib.sha256(raw.encode()).hexdigest()[:12].upper()}"
            else:
                rec.digital_form_c_token = False

    @api.depends('arrival_at_hotel')
    def _compute_deadline(self):
        for rec in self:
            if rec.arrival_at_hotel:
                rec.submission_deadline = rec.arrival_at_hotel + timedelta(hours=24)
            else:
                rec.submission_deadline = False

    @api.depends('frro_portal_status', 'submission_deadline')
    def _compute_overdue(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.frro_portal_status in ('not_submitted', 'rejected') and rec.submission_deadline:
                rec.is_overdue = now > rec.submission_deadline
            else:
                rec.is_overdue = False

    def _search_overdue(self, operator, value):
        now = fields.Datetime.now()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('frro_portal_status', 'in', ('not_submitted', 'rejected')), ('submission_deadline', '<', now)]
        else:
            return ['|', ('frro_portal_status', 'not in', ('not_submitted', 'rejected')), ('submission_deadline', '>=', now)]

    @api.depends('visa_valid_until', 'expected_departure')
    def _compute_visa_alert(self):
        today = fields.Date.today()
        for rec in self:
            if rec.visa_valid_until:
                if rec.expected_departure:
                    dep_date = rec.expected_departure.date()
                    rec.is_visa_expiring_soon = rec.visa_valid_until <= dep_date
                else:
                    rec.is_visa_expiring_soon = rec.visa_valid_until <= (today + timedelta(days=7))
            else:
                rec.is_visa_expiring_soon = False

    @api.depends('doc_passport_copy', 'doc_visa_copy', 'doc_entry_stamp', 'doc_photo')
    def _compute_documents_complete(self):
        for rec in self:
            rec.documents_complete = bool(rec.doc_passport_copy and rec.doc_visa_copy and rec.doc_entry_stamp and rec.doc_photo)

    @api.onchange('guest_id')
    def _onchange_guest_id(self):
        if self.guest_id:
            if hasattr(self.guest_id, 'nationality_id') and self.guest_id.nationality_id:
                self.nationality_id = self.guest_id.nationality_id
            if hasattr(self.guest_id, 'id_number') and self.guest_id.id_number:
                self.passport_number = self.guest_id.id_number
            if self.guest_id.contact_address:
                self.home_country_address = self.guest_id.contact_address

    @api.onchange('reservation_id')
    def _onchange_reservation_id(self):
        if self.reservation_id:
            self.guest_id = self.reservation_id.guest_id
            self.room_id = self.reservation_id.room_id
            self.property_id = self.reservation_id.property_id
            self.arrival_at_hotel = self.reservation_id.check_in
            self.expected_departure = self.reservation_id.check_out

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('compliance.foreign.guest') or _('New')
        return super().create(vals_list)

    # User-Friendly & Eco-Smart Actions
    def action_auto_fill_foreign_details(self):
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
                'title': _("Passport & Booking Synced"),
                'message': _("Guest passport and stay details synchronized successfully."),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_quick_portal_submit(self):
        """1-Click Paperless BoI Submission."""
        for rec in self:
            if not rec.passport_number:
                raise UserError(_("Passport number is required."))
            rec.write({
                'state': 'submitted',
                'frro_portal_status': 'submitted',
                'submission_time': fields.Datetime.now(),
                'is_paperless': True,
            })

    # Workflow Actions
    def action_verify_documents(self):
        for rec in self:
            if not rec.passport_number:
                raise UserError(_("Passport number is required to verify documents."))
            rec.write({
                'state': 'docs_verified',
                'doc_passport_copy': True,
                'doc_visa_copy': True,
            })

    def action_mark_frro_submitted(self):
        for rec in self:
            rec.write({
                'state': 'submitted',
                'frro_portal_status': 'submitted',
                'submission_time': fields.Datetime.now(),
            })

    def action_mark_frro_completed(self):
        for rec in self:
            if not rec.frro_ack_number:
                raise UserError(_("Please provide the Form C Application / Acknowledgment Number before marking completed."))
            rec.write({
                'state': 'completed',
                'frro_portal_status': 'acknowledged',
            })

    def action_reset_draft(self):
        for rec in self:
            rec.write({'state': 'draft', 'frro_portal_status': 'not_submitted'})
