# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipPaymentWizard(models.TransientModel):
    _name = 'hr.payslip.payment.wizard'
    _description = 'Register Salary Payment Wizard'

    payslip_ids = fields.Many2many('hr.payslip', string='Selected Payslips', required=True)
    payment_date = fields.Date('Payment Date', required=True, default=fields.Date.today)
    payment_method = fields.Selection([
        ('bank', 'Bank Transfer (NEFT/RTGS/IMPS/Wire)'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ], string='Disbursement Method', default='bank', required=True)
    payment_reference = fields.Char('Reference / UTR / Cheque No.', help="Bank transaction reference or cheque number.")
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        domain=[('type', 'in', ('bank', 'cash'))],
        help="Optional bank or cash journal to record the payment."
    )
    amount_total = fields.Monetary('Total Disbursement Amount', compute='_compute_amount_total', readonly=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    @api.depends('payslip_ids.net_wage')
    def _compute_amount_total(self):
        for wizard in self:
            wizard.amount_total = sum(slip.net_wage for slip in wizard.payslip_ids)

    def action_confirm_payment(self):
        self.ensure_one()
        if not self.payslip_ids:
            raise UserError(_("No payslips selected to pay."))

        for slip in self.payslip_ids:
            # Confirm if not already confirmed
            if slip.state in ('draft', 'verify'):
                slip.action_payslip_done()

            slip.write({
                'payment_date': self.payment_date,
                'payment_method': self.payment_method,
                'payment_reference': self.payment_reference,
                'journal_id': self.journal_id.id if self.journal_id else False,
                'state': 'paid',
            })

            # Check if all slips in the parent batch are paid
            if slip.payslip_run_id:
                run = slip.payslip_run_id
                if all(s.state == 'paid' for s in run.slip_ids):
                    run.state = 'paid'

        return {'type': 'ir.actions.act_window_close'}
