# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ComplianceSecurityLog(models.Model):
    _name = 'compliance.security.log'
    _description = 'Resort Security, Visitor & Vehicle Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'entry_datetime desc, id desc'

    name = fields.Char(
        string='Security Log ID',
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    log_type = fields.Selection([
        ('visitor', 'Non-Resident Visitor Register'),
        ('vehicle', 'Vehicle Entry / Exit Log'),
        ('patrol', 'Security Patrol Check'),
        ('cctv', 'CCTV Monitoring & Review'),
        ('lost_found', 'Lost & Found Custody Log'),
        ('key_control', 'Master Key & Access Control'),
        ('contractor', 'Contractor / Vendor Gate Pass'),
    ], string='Log Type', default='visitor', required=True, tracking=True)

    entry_datetime = fields.Datetime(string='Entry / Log Time', default=fields.Datetime.now, required=True, tracking=True)
    exit_datetime = fields.Datetime(string='Exit / Return Time', tracking=True)
    
    property_id = fields.Many2one('hotel.property', string='Property / Resort', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    security_officer_id = fields.Many2one('res.users', string='Duty Security Officer', default=lambda self: self.env.user, tracking=True)
    
    shift = fields.Selection([
        ('morning', 'Morning Shift (06:00 - 14:00)'),
        ('evening', 'Evening Shift (14:00 - 22:00)'),
        ('night', 'Night Shift (22:00 - 06:00)'),
    ], string='Duty Shift', default='morning', required=True, tracking=True)

    # Visitor
    visitor_name = fields.Char(string='Visitor / Person Name', tracking=True)
    visitor_phone = fields.Char(string='Visitor Mobile / Phone', tracking=True)
    visitor_id_proof = fields.Char(string='ID Proof Type & No (Aadhaar / Driving Lic)')
    visiting_guest_id = fields.Many2one('res.partner', string='Resort Guest Visited', tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room Visited')
    purpose_of_visit = fields.Char(string='Purpose / Destination on Site')

    # Vehicle & Green Transport
    vehicle_number = fields.Char(string='Vehicle Plate Number', tracking=True)
    vehicle_type = fields.Selection([
        ('car', 'Private Car / Sedan'),
        ('suv', 'SUV / MPV'),
        ('taxi', 'Commercial Taxi / Cab'),
        ('two_wheeler', 'Motorcycle / Scooter'),
        ('bus', 'Tourist Bus / Coach'),
        ('delivery', 'Delivery Van / Goods Truck'),
        ('other', 'Other Vehicle'),
    ], string='Vehicle Category', default='car')
    eco_transport_type = fields.Selection([
        ('standard', 'Fuel / Fossil (Petrol/Diesel)'),
        ('ev', 'Electric Vehicle (EV)'),
        ('hybrid', 'Hybrid Electric'),
        ('bicycle', 'Bicycle / Non-Motorized'),
    ], string='Eco / Fuel Category', default='standard', tracking=True)
    is_ev_vehicle = fields.Boolean(string='EV Vehicle', compute='_compute_is_ev', store=True)
    allocated_ev_charging = fields.Boolean(string='Allocated to EV Charging Bay', default=False)
    driver_name = fields.Char(string='Driver Name')
    parking_slot = fields.Char(string='Parking Bay / Slot')
    is_paperless_gate_pass = fields.Boolean(string='Paperless e-Gate Pass', default=True)

    # Patrol & Keys & Assets
    key_name = fields.Char(string='Master Key / Card Tag')
    patrol_zone = fields.Char(string='Patrol Zone / Checkpoint')
    item_description = fields.Text(string='Item / Asset Description')
    observations = fields.Text(string='Observations / Security Notes')

    state = fields.Selection([
        ('active', 'Active / On Premises'),
        ('departed', 'Departed / Handed Over'),
        ('flagged', 'Flagged / Security Alert'),
    ], string='Status', default='active', tracking=True)

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'compliance_security_log_attachment_rel',
        'log_id',
        'attachment_id',
        string='Photos, Gate Passes or Scans'
    )

    @api.depends('eco_transport_type')
    def _compute_is_ev(self):
        for rec in self:
            rec.is_ev_vehicle = rec.eco_transport_type in ('ev', 'hybrid')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('compliance.security.log') or _('New')
        return super().create(vals_list)

    def action_mark_departed(self):
        self.write({
            'state': 'departed',
            'exit_datetime': self.exit_datetime or fields.Datetime.now()
        })

    def action_flag_alert(self):
        self.write({'state': 'flagged'})
