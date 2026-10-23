# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class CompliancePoliceVisit(models.Model):
    _name = 'compliance.police.visit'
    _description = 'Resort Police & Law Enforcement Official Visit Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'visit_datetime desc, id desc'

    name = fields.Char(
        string='Visit Record ID',
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    visit_datetime = fields.Datetime(string='Arrival Date & Time', default=fields.Datetime.now, required=True, tracking=True)
    departure_datetime = fields.Datetime(string='Departure Date & Time', tracking=True)
    police_station = fields.Char(string='Police Station / Unit', required=True, tracking=True, help="e.g. North Goa PS, Calangute Police Station, Cyber Cell")

    officer_name = fields.Char(string='Officer Name', required=True, tracking=True)
    officer_rank = fields.Selection([
        ('constable', 'Police Constable (PC)'),
        ('head_constable', 'Head Constable (HC)'),
        ('asi', 'Assistant Sub-Inspector (ASI)'),
        ('psi', 'Police Sub-Inspector (PSI)'),
        ('pi', 'Police Inspector (PI) / SHO'),
        ('dy_sp', 'Deputy SP / ACP'),
        ('sp', 'Superintendent of Police (SP)'),
        ('cid_crime', 'CID / Crime Branch / Special Branch'),
        ('other', 'Other Rank / Armed Police'),
    ], string='Officer Rank', default='psi', required=True, tracking=True)

    officer_badge_no = fields.Char(string='Badge / Belt / ID Number', tracking=True)
    officer_phone = fields.Char(string='Officer Mobile / Contact Number', tracking=True)

    purpose = fields.Selection([
        ('routine_patrol', 'Routine Night / Day Patrol Check'),
        ('guest_verification', 'Guest Document / Identity Verification'),
        ('incident_inquiry', 'Incident / Case Investigation Inquiry'),
        ('vip_security', 'VIP / Dignitary Security Protocol'),
        ('summons_notice', 'Legal Notice / Summons Service'),
        ('cctv_inquiry', 'CCTV Footage Review Request'),
        ('license_check', 'Resort License / Excise Compliance Check'),
        ('other', 'Other Official Police Interaction'),
    ], string='Purpose of Police Visit', default='routine_patrol', required=True, tracking=True)

    incident_id = fields.Many2one('compliance.incident', string='Related Incident / Case Ref', tracking=True)
    met_with_id = fields.Many2one('res.users', string='Resort Official Met (GM / Security Head)', default=lambda self: self.env.user, tracking=True)
    property_id = fields.Many2one('hotel.property', string='Property / Resort', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    general_diary_entry = fields.Char(string='Police Station GD Entry No')
    observations = fields.Text(string='Police Instructions & Meeting Summary', required=True)
    
    follow_up_required = fields.Boolean(string='Follow-Up Action Required', default=False, tracking=True)
    follow_up_notes = fields.Text(string='Follow-Up Action Plan')

    state = fields.Selection([
        ('draft', 'Visit Logged'),
        ('in_progress', 'Action In Progress'),
        ('completed', 'Completed & Verified'),
    ], string='Status', default='draft', tracking=True)

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'compliance_police_visit_attachment_rel',
        'visit_id',
        'attachment_id',
        string='Written Notices, Summons or Documents'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('compliance.police.visit') or _('New')
        return super().create(vals_list)

    def action_start_action(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({
            'state': 'completed',
            'departure_datetime': self.departure_datetime or fields.Datetime.now()
        })
