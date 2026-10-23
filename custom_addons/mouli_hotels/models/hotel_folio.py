# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HotelFolio(models.Model):
    _name = 'hotel.folio'
    _description = 'Hotel Guest Folio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Folio No', copy=False, readonly=True, default=lambda self: _('New'))
    reservation_id = fields.Many2one('hotel.reservation', string='Reservation', readonly=True)
    guest_id = fields.Many2one('res.partner', string='Guest', required=True, tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room', tracking=True)
    property_id = fields.Many2one('hotel.property', string='Property', required=True)
    company_id = fields.Many2one('res.company', related='property_id.company_id', string='Company', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency', readonly=True)

    date_order = fields.Datetime(string='Folio Date', default=fields.Datetime.now, required=True)
    line_ids = fields.One2many('hotel.folio.line', 'folio_id', string='Charge Lines')
    payment_ids = fields.One2many('hotel.folio.payment', 'folio_id', string='Payments & Advances')

    amount_total = fields.Monetary(string='Total Charges', compute='_compute_financials', store=True, currency_field='currency_id')
    amount_paid = fields.Monetary(string='Total Paid', compute='_compute_financials', store=True, currency_field='currency_id')
    amount_due = fields.Monetary(string='Balance Due', compute='_compute_financials', store=True, currency_field='currency_id')

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid / Cleared')
    ], string='Payment Status', compute='_compute_financials', store=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Open'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid & Cleared'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    invoice_id = fields.Many2one('account.move', string='Customer Invoice', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hotel.folio') or _('New')
        return super().create(vals_list)

    @api.depends('line_ids.price_subtotal', 'payment_ids.amount')
    def _compute_financials(self):
        for folio in self:
            total = sum(folio.line_ids.mapped('price_subtotal'))
            paid = sum(folio.payment_ids.mapped('amount'))
            folio.amount_total = total
            folio.amount_paid = paid
            due = total - paid
            folio.amount_due = max(0.0, due)
            if paid <= 0:
                folio.payment_status = 'unpaid'
            elif paid >= total - 0.01 and total > 0:
                folio.payment_status = 'paid'
            elif paid > 0:
                folio.payment_status = 'partial'
            else:
                folio.payment_status = 'unpaid'

    def action_register_payment(self):
        self.ensure_one()
        return {
            'name': _('Register Payment for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.folio.payment',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_folio_id': self.id,
                'default_amount': self.amount_due,
            }
        }

    def action_quick_settle_cash(self):
        self.ensure_one()
        if self.amount_due > 0:
            self.env['hotel.folio.payment'].create({
                'folio_id': self.id,
                'name': _('Full Cash Settlement'),
                'amount': self.amount_due,
                'payment_method': 'cash',
                'reference': 'Cash at Front Desk',
            })
            self._compute_financials()

    def action_quick_settle_upi(self):
        self.ensure_one()
        if self.amount_due > 0:
            self.env['hotel.folio.payment'].create({
                'folio_id': self.id,
                'name': _('UPI / QR Full Settlement'),
                'amount': self.amount_due,
                'payment_method': 'upi',
                'reference': 'UPI QR Payment',
            })
            self._compute_financials()

    def action_print_bill(self):
        self.ensure_one()
        return self.env.ref('mouli_hotels.action_report_hotel_folio_bill').report_action(self)

    def action_create_invoice(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Cannot generate an invoice for an empty folio."))
        if self.invoice_id:
            raise UserError(_("Invoice %s has already been created for this folio.") % self.invoice_id.name)

        invoice_lines = []
        for line in self.line_ids:
            invoice_lines.append((0, 0, {
                'name': line.name or 'Hotel Service',
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'product_id': line.product_id.id if line.product_id else False,
            }))

        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.guest_id.id,
            'invoice_date': fields.Date.context_today(self),
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'invoice_line_ids': invoice_lines,
        }

        invoice = self.env['account.move'].create(move_vals)
        self.write({
            'invoice_id': invoice.id,
            'state': 'invoiced',
        })
        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
        }

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
        }


class HotelFolioLine(models.Model):
    _name = 'hotel.folio.line'
    _description = 'Hotel Folio Charge Line'

    folio_id = fields.Many2one('hotel.folio', string='Folio', required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='folio_id.currency_id', readonly=True)
    name = fields.Char(string='Description / Service', required=True)
    service_type = fields.Selection([
        ('room', 'Room Accommodation'),
        ('restaurant', 'Restaurant / F&B'),
        ('bar', 'Bar & Beverage'),
        ('spa', 'Spa & Wellness'),
        ('activity', 'Activities & Recreation'),
        ('laundry', 'Laundry'),
        ('minibar', 'Minibar'),
        ('other', 'Other Services')
    ], string='Service Type', default='room', required=True)

    product_id = fields.Many2one('product.product', string='Product Reference')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Monetary(string='Unit Price', required=True, currency_field='currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal', store=True, currency_field='currency_id')

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = (line.quantity or 0.0) * (line.price_unit or 0.0)


class HotelFolioPayment(models.Model):
    _name = 'hotel.folio.payment'
    _description = 'Hotel Folio Payment / Advance'
    _order = 'payment_date desc, id desc'

    name = fields.Char(string='Payment Title', default=lambda self: _('Payment Receipt'))
    folio_id = fields.Many2one('hotel.folio', string='Folio', required=True, ondelete='cascade')
    guest_id = fields.Many2one('res.partner', related='folio_id.guest_id', string='Guest', readonly=True)
    currency_id = fields.Many2one('res.currency', related='folio_id.currency_id', readonly=True)
    payment_date = fields.Datetime(string='Payment Date', default=fields.Datetime.now, required=True)
    amount = fields.Monetary(string='Amount Paid', required=True, currency_field='currency_id')
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit / Debit Card'),
        ('upi', 'UPI / QR Code / Online'),
        ('bank', 'Bank Transfer')
    ], string='Payment Method', default='cash', required=True)
    reference = fields.Char(string='Transaction ID / Reference')
    is_advance = fields.Boolean(string='Booking Advance Deposit', default=False)
