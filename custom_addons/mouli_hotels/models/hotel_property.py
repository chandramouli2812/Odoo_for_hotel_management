# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HotelProperty(models.Model):
    _name = 'hotel.property'
    _description = 'Hotel Property / Resort'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Property Name', required=True, tracking=True)
    code = fields.Char(string='Property Code', required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency', readonly=True
    )
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='Zip Code')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    active = fields.Boolean(default=True)
    image_1920 = fields.Image(string='Property Photo')
    address = fields.Char(string='Full Address', compute='_compute_address')

    @api.depends('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def _compute_address(self):
        for prop in self:
            parts = [p for p in [
                prop.street,
                prop.street2,
                prop.city,
                prop.state_id.name if prop.state_id else '',
                prop.zip,
                prop.country_id.name if prop.country_id else ''
            ] if p]
            prop.address = ', '.join(parts) if parts else ''

    building_ids = fields.One2many('hotel.building', 'property_id', string='Buildings / Wings')
    floor_ids = fields.One2many('hotel.floor', 'property_id', string='Floors')
    room_ids = fields.One2many('hotel.room', 'property_id', string='Rooms')

    total_rooms = fields.Integer(string='Total Rooms', compute='_compute_room_stats', store=True)
    occupied_rooms = fields.Integer(string='Occupied Rooms', compute='_compute_room_stats', store=True)
    available_rooms = fields.Integer(string='Available Rooms', compute='_compute_room_stats', store=True)

    @api.depends('room_ids', 'room_ids.occupancy_status', 'room_ids.active')
    def _compute_room_stats(self):
        for prop in self:
            active_rooms = prop.room_ids.filtered(lambda r: r.active)
            prop.total_rooms = len(active_rooms)
            prop.occupied_rooms = len(active_rooms.filtered(lambda r: r.occupancy_status == 'occupied'))
            prop.available_rooms = len(active_rooms.filtered(
                lambda r: r.occupancy_status == 'vacant' and r.housekeeping_status in ('clean', 'inspected') and r.maintenance_status == 'operational'
            ))

    _code_unique = models.Constraint(
        'UNIQUE (code)',
        'The Property Code must be unique!'
    )


class HotelBuilding(models.Model):
    _name = 'hotel.building'
    _description = 'Hotel Building / Wing / Villa'

    name = fields.Char(string='Building Name', required=True)
    code = fields.Char(string='Building Code')
    property_id = fields.Many2one('hotel.property', string='Property', required=True, ondelete='cascade')
    floor_count = fields.Integer(string='Number of Floors', default=1)
    floor_ids = fields.One2many('hotel.floor', 'building_id', string='Floors')
    room_ids = fields.One2many('hotel.room', 'building_id', string='Rooms')


class HotelFloor(models.Model):
    _name = 'hotel.floor'
    _description = 'Hotel Floor'

    name = fields.Char(string='Floor Name', required=True)
    floor_number = fields.Integer(string='Floor Number', default=1)
    property_id = fields.Many2one('hotel.property', string='Property', required=True, ondelete='cascade')
    building_id = fields.Many2one('hotel.building', string='Building', ondelete='set null')
    room_ids = fields.One2many('hotel.room', 'floor_id', string='Rooms')
