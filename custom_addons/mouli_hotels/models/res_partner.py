# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_hotel_guest = fields.Boolean(string='Is Hotel Guest', default=False)
    id_type = fields.Selection([
        ('passport', 'Passport'),
        ('national_id', 'National ID / Aadhaar'),
        ('driving_license', 'Driving License'),
        ('other', 'Other')
    ], string='ID Document Type')
    id_number = fields.Char(string='ID Document Number')
    nationality_id = fields.Many2one('res.country', string='Nationality')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    birthdate = fields.Date(string='Date of Birth')
    vip_status = fields.Selection([
        ('standard', 'Standard'),
        ('silver', 'Silver VIP'),
        ('gold', 'Gold VIP'),
        ('platinum', 'Platinum VIP')
    ], string='VIP Status', default='standard')
    preferred_room_type_id = fields.Many2one('hotel.room.type', string='Preferred Room Type')
    guest_notes = fields.Text(string='Guest Preferences / Notes')
    reservation_count = fields.Integer(string='Stay Count', compute='_compute_reservation_count')

    def _compute_reservation_count(self):
        for partner in self:
            partner.reservation_count = self.env['hotel.reservation'].search_count([
                ('guest_id', '=', partner.id)
            ])

    def action_view_guest_reservations(self):
        self.ensure_one()
        return {
            'name': 'Guest Reservations',
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('guest_id', '=', self.id)],
            'context': {'default_guest_id': self.id},
        }
