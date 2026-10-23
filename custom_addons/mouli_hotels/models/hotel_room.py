# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'room_number'

    name = fields.Char(string='Room Display Name', compute='_compute_name', store=True)
    room_number = fields.Char(string='Room Number', required=True, tracking=True)
    property_id = fields.Many2one('hotel.property', string='Property', required=True, tracking=True)
    building_id = fields.Many2one('hotel.building', string='Building / Wing', domain="[('property_id', '=', property_id)]")
    floor_id = fields.Many2one('hotel.floor', string='Floor', domain="[('property_id', '=', property_id)]")
    room_type_id = fields.Many2one('hotel.room.type', string='Room Type', required=True, tracking=True)

    company_id = fields.Many2one('res.company', related='property_id.company_id', string='Company', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency', readonly=True)
    list_price = fields.Monetary(related='room_type_id.list_price', string='Daily Rate', readonly=True)
    capacity = fields.Integer(related='room_type_id.capacity', string='Capacity', readonly=True)

    # 3-Axis Status Architecture
    occupancy_status = fields.Selection([
        ('vacant', 'Vacant'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied')
    ], string='Occupancy Status', default='vacant', required=True, tracking=True)

    housekeeping_status = fields.Selection([
        ('clean', 'Clean'),
        ('dirty', 'Dirty'),
        ('cleaning', 'Cleaning In Progress'),
        ('inspected', 'Inspected & Ready')
    ], string='Housekeeping Status', default='clean', required=True, tracking=True)

    maintenance_status = fields.Selection([
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('out_of_service', 'Out of Service')
    ], string='Maintenance Status', default='operational', required=True, tracking=True)

    is_available = fields.Boolean(
        string='Available for Check-in', compute='_compute_is_available', store=True
    )

    current_reservation_id = fields.Many2one(
        'hotel.reservation', string='Current Reservation', readonly=True, copy=False
    )
    current_guest_id = fields.Many2one(
        'res.partner', related='current_reservation_id.guest_id', string='Current Guest', readonly=True
    )

    active = fields.Boolean(default=True)
    notes = fields.Text(string='Internal Notes')

    @api.depends('room_number', 'room_type_id', 'property_id')
    def _compute_name(self):
        for room in self:
            type_name = room.room_type_id.name if room.room_type_id else ''
            room.name = f"Room {room.room_number or ''} ({type_name})"

    @api.depends('occupancy_status', 'housekeeping_status', 'maintenance_status')
    def _compute_is_available(self):
        for room in self:
            room.is_available = (
                room.occupancy_status == 'vacant' and
                room.housekeeping_status in ('clean', 'inspected') and
                room.maintenance_status == 'operational'
            )

    _room_number_prop_unique = models.Constraint(
        'UNIQUE (room_number, property_id)',
        'Room number must be unique within the same property!'
    )

    def action_set_clean(self):
        self.write({'housekeeping_status': 'clean'})

    def action_set_dirty(self):
        self.write({'housekeeping_status': 'dirty'})

    def action_set_inspected(self):
        self.write({'housekeeping_status': 'inspected'})

    def action_set_maintenance(self):
        self.write({'maintenance_status': 'maintenance'})

    def action_set_operational(self):
        self.write({'maintenance_status': 'operational'})

    def action_quick_book(self):
        self.ensure_one()
        return {
            'name': _('New Booking - Room %s') % self.room_number,
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
            'context': {
                'default_property_id': self.property_id.id,
                'default_room_type_id': self.room_type_id.id,
                'default_room_id': self.id,
                'default_check_in': fields.Datetime.now(),
                'default_rate_per_night': self.list_price,
            }
        }

    def action_view_current_stay(self):
        self.ensure_one()
        if self.current_reservation_id:
            return {
                'name': _('Active Stay - Room %s') % self.room_number,
                'type': 'ir.actions.act_window',
                'res_model': 'hotel.reservation',
                'res_id': self.current_reservation_id.id,
                'view_mode': 'form',
                'views': [(False, 'form')],
            }
        return False
