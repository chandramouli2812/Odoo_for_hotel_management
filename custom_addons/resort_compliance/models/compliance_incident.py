# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ComplianceIncident(models.Model):
    _name = 'compliance.incident'
    _description = 'Resort Security & Police Incident Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'incident_date desc, id desc'

    name = fields.Char(
        string='Incident Reference',
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    incident_type = fields.Selection([
        ('theft', 'Theft / Missing Property'),
        ('lost_found', 'Lost & Found Case'),
        ('guest_dispute', 'Guest Dispute / Altercation'),
        ('staff_dispute', 'Employee / Staff Conflict'),
        ('accident', 'Accident / Physical Injury'),
        ('property_damage', 'Resort Property Damage'),
        ('unauthorized_entry', 'Unauthorized Entry / Trespassing'),
        ('suspicious_activity', 'Suspicious Activity / Security Alert'),
        ('missing_person', 'Missing Person / Overdue Guest'),
        ('medical_emergency', 'Medical Emergency / Ambulance Called'),
        ('fire_safety', 'Fire / Safety / Hazard Incident'),
        ('assault', 'Assault / Serious Crime'),
        ('noise_nuisance', 'Noise Violation / Public Nuisance'),
        ('other', 'Other Incident'),
    ], string='Incident Category', default='theft', required=True, tracking=True)

    severity = fields.Selection([
        ('low', 'Low / Minor Log'),
        ('medium', 'Medium Incident'),
        ('high', 'High / Police Inquired'),
        ('critical', 'Critical / FIR Registered / Emergency'),
    ], string='Severity Level', default='low', required=True, tracking=True)

    summary = fields.Char(string='Brief Headline / Summary', required=True, tracking=True)
    incident_date = fields.Datetime(string='Date & Time of Incident', default=fields.Datetime.now, required=True, tracking=True)
    reported_date = fields.Datetime(string='Date & Time Reported', default=fields.Datetime.now, tracking=True)
    reported_by_id = fields.Many2one('res.users', string='Reported By', default=lambda self: self.env.user, tracking=True)

    location = fields.Char(string='Location / Resort Area', required=True, tracking=True, help="e.g. Room 204, Pool Deck, Beachside Restaurant, Main Lobby")
    property_id = fields.Many2one('hotel.property', string='Property / Resort', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Involvements
    guest_id = fields.Many2one('res.partner', string='Guest Involved', tracking=True)
    reservation_id = fields.Many2one('hotel.reservation', string='Related Reservation', tracking=True)
    room_id = fields.Many2one('hotel.room', string='Related Room', tracking=True)
    persons_involved = fields.Text(string='Witnesses & Persons Involved (Names, Phone Nos, IDs)')

    description = fields.Text(string='Detailed Incident Description & Sequence of Events')
    action_taken = fields.Text(string='Immediate Action Taken by Resort Staff & Security')
    evidence_notes = fields.Text(string='Evidence Log (CCTV footage recordings, photographs, physical items held)')

    # Police & FIR
    police_reported = fields.Boolean(string='Reported to Police', default=False, tracking=True)
    police_station_name = fields.Char(string='Police Station Name', tracking=True)
    police_reported_datetime = fields.Datetime(string='Police Notification Timestamp')
    police_diary_gd_no = fields.Char(string='Station General Diary (GD) Entry No', tracking=True)

    fir_registered = fields.Boolean(string='Official FIR Registered', default=False, tracking=True)
    fir_number = fields.Char(string='FIR / Crime Case Number', tracking=True)
    fir_date = fields.Date(string='FIR Registration Date', tracking=True)
    investigating_officer = fields.Char(string='Investigating Officer (IO) Name & Badge')
    io_contact = fields.Char(string='IO Phone / Contact No')

    police_visit_ids = fields.One2many(
        'compliance.police.visit',
        'incident_id',
        string='Police Visits for this Incident'
    )
    police_visit_count = fields.Integer(string='Police Visits', compute='_compute_police_visit_count')

    # Resolution & Closure
    resolution_summary = fields.Text(string='Investigation Findings & Final Resolution')
    closed_date = fields.Datetime(string='Closure Timestamp')
    closed_by_id = fields.Many2one('res.users', string='Closed By')

    state = fields.Selection([
        ('draft', 'Incident Reported'),
        ('investigating', 'Internal Investigation'),
        ('police_notified', 'Police Notified'),
        ('fir_lodged', 'FIR Lodged / Active Police Case'),
        ('legal', 'Legal / Court Proceeding'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed & Archived'),
    ], string='Status', default='draft', required=True, tracking=True)

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'compliance_incident_attachment_rel',
        'incident_id',
        'attachment_id',
        string='CCTV Images, FIR Copies & Evidence'
    )

    def _compute_police_visit_count(self):
        for rec in self:
            rec.police_visit_count = len(rec.police_visit_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('compliance.incident') or _('New')
        return super().create(vals_list)

    # Workflow Actions
    def action_investigate(self):
        self.write({'state': 'investigating'})

    def action_notify_police(self):
        self.write({
            'state': 'police_notified',
            'police_reported': True,
            'police_reported_datetime': fields.Datetime.now()
        })

    def action_lodge_fir(self):
        for rec in self:
            if not rec.fir_number:
                raise UserError(_("Please provide the FIR Number before moving to FIR Lodged status."))
            rec.write({
                'state': 'fir_lodged',
                'fir_registered': True,
                'fir_date': rec.fir_date or fields.Date.today()
            })

    def action_legal(self):
        self.write({'state': 'legal'})

    def action_resolve(self):
        self.write({'state': 'resolved'})

    def action_close(self):
        self.write({
            'state': 'closed',
            'closed_date': fields.Datetime.now(),
            'closed_by_id': self.env.user.id
        })

    def action_reopen(self):
        self.write({'state': 'investigating'})
