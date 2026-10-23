# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HotelRoomType(models.Model):
    _name = 'hotel.room.type'
    _description = 'Hotel Room Type'
    _inherit = ['mail.thread']

    name = fields.Char(string='Room Type Name', required=True, tracking=True)
    code = fields.Char(string='Type Code', required=True)
    capacity = fields.Integer(string='Max Capacity', default=2, required=True)
    adult_capacity = fields.Integer(string='Adults Capacity', default=2, required=True)
    child_capacity = fields.Integer(string='Children Capacity', default=1)
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency', readonly=True)
    list_price = fields.Monetary(string='Base Rate Per Night', required=True, default=1000.0, currency_field='currency_id')

    description = fields.Html(string='Description')
    amenity_ids = fields.Many2many('hotel.amenity', string='Amenities')
    room_ids = fields.One2many('hotel.room', 'room_type_id', string='Assigned Rooms')
    room_count = fields.Integer(string='Room Count', compute='_compute_room_count')
    image_1920 = fields.Image(string='Room Type Image')

    @api.depends('room_ids')
    def _compute_room_count(self):
        for record in self:
            record.room_count = len(record.room_ids)

    # Website Publishing & Leads
    is_published = fields.Boolean(string='Published on Website', default=True, copy=False, tracking=True)
    website_short_description = fields.Char(string='Website Tagline / Quick Highlight', help="E.g., Panoramic Oceanfront Sunrise View with Private Plunge Pool")
    website_features = fields.Text(string='Key Highlights / Inclusions', help="E.g., Private Infinity Pool, Ocean Balcony, King Size Bed, Complimentary Breakfast, High-Speed Wi-Fi")
    website_ribbon = fields.Selection([
        ('luxury', 'Ultra Luxury'),
        ('popular', 'Most Popular'),
        ('featured', 'Featured'),
        ('deal', 'Best Value'),
        ('beachfront', 'Beachfront'),
    ], string='Website Ribbon Badge', default='featured')
    website_sequence = fields.Integer(string='Website Display Order', default=10)
    website_url = fields.Char(string='Website URL', compute='_compute_website_url')
    website_inquiry_count = fields.Integer(string='Web Inquiries', compute='_compute_inquiry_count')

    def _compute_website_url(self):
        for rec in self:
            rec.website_url = f"/rooms/{rec.id}"

    def _compute_inquiry_count(self):
        for rec in self:
            rec.website_inquiry_count = self.env['hotel.reservation'].search_count([
                ('room_type_id', '=', rec.id),
                ('booking_source', '=', 'website')
            ])

    def action_view_website_inquiries(self):
        self.ensure_one()
        return {
            'name': f"Website Inquiries - {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'domain': [('room_type_id', '=', self.id), ('booking_source', '=', 'website')],
            'context': {'default_room_type_id': self.id, 'default_booking_source': 'website'},
        }

    def action_open_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/rooms/{self.id}',
            'target': 'new',
        }

    _code_unique = models.Constraint(
        'UNIQUE (code)',
        'The Room Type Code must be unique!'
    )


class HotelAmenity(models.Model):
    _name = 'hotel.amenity'
    _description = 'Hotel Amenity'

    name = fields.Char(string='Amenity Name', required=True)
    code = fields.Char(string='Amenity Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
