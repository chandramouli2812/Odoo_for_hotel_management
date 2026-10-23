# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HotelQuickCheckoutWizard(models.TransientModel):
    _name = 'hotel.quick.checkout.wizard'
    _description = 'Hotel Quick Settle & Checkout Wizard'

    reservation_id = fields.Many2one('hotel.reservation', string='Reservation', required=True, readonly=True)
    folio_id = fields.Many2one('hotel.folio', related='reservation_id.folio_id', string='Guest Folio', readonly=True)
    guest_id = fields.Many2one('res.partner', related='reservation_id.guest_id', string='Guest', readonly=True)
    room_id = fields.Many2one('hotel.room', related='reservation_id.room_id', string='Room', readonly=True)
    currency_id = fields.Many2one('res.currency', related='reservation_id.currency_id', readonly=True)

    amount_total = fields.Monetary(related='folio_id.amount_total', string='Total Charges', readonly=True)
    amount_paid = fields.Monetary(related='folio_id.amount_paid', string='Already Paid', readonly=True)
    amount_due = fields.Monetary(related='folio_id.amount_due', string='Outstanding Balance', readonly=True)

    payment_amount = fields.Monetary(
        string='Settlement Amount', required=True, currency_field='currency_id',
        help="Amount collected right now to clear the remaining balance."
    )
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit / Debit Card'),
        ('upi', 'UPI / QR Code / Online'),
        ('bank', 'Bank Transfer')
    ], string='Payment Method', default='cash', required=True)

    reference = fields.Char(string='Transaction Ref / Notes')
    print_bill = fields.Boolean(string='Print Folio Bill after Checkout', default=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self._context.get('active_id')
        if active_id and self._context.get('active_model') == 'hotel.reservation':
            res_obj = self.env['hotel.reservation'].browse(active_id)
            res['reservation_id'] = res_obj.id
            if res_obj.folio_id:
                res['payment_amount'] = res_obj.folio_id.amount_due
        return res

    def action_settle_and_checkout(self):
        self.ensure_one()
        res = self.reservation_id
        folio = res.folio_id

        if self.payment_amount > 0 and folio:
            self.env['hotel.folio.payment'].create({
                'folio_id': folio.id,
                'name': f"Checkout Settlement for {res.name}",
                'amount': self.payment_amount,
                'payment_method': self.payment_method,
                'reference': self.reference or 'Checkout Payment',
                'is_advance': False,
            })
            folio._compute_financials()

        # Complete Checkout
        res._execute_checkout()

        if self.print_bill and folio:
            return self.env.ref('mouli_hotels.action_report_hotel_folio_bill').report_action(folio)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Checkout Completed'),
                'message': _('Guest %s successfully checked out. Room %s is now vacant and assigned to housekeeping.') % (res.guest_id.name, res.room_id.name),
                'type': 'success',
                'sticky': False,
            }
        }
