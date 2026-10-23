# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrPayslipLine(models.Model):
    _name = 'hr.payslip.line'
    _description = 'Payslip Line'
    _order = 'payslip_id, sequence, id'

    name = fields.Char('Rule Description', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade', index=True)
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule')
    code = fields.Char('Code', required=True)
    category_id = fields.Many2one('hr.salary.rule.category', string='Category', required=True)
    sequence = fields.Integer('Sequence', default=5)
    quantity = fields.Float('Quantity', default=1.0)
    rate = fields.Float('Rate (%)', default=100.0)
    amount = fields.Monetary('Base Amount', default=0.0)
    total = fields.Monetary('Total Calculated', compute='_compute_total', store=True)
    appears_on_payslip = fields.Boolean('Appears on Payslip', default=True)

    company_id = fields.Many2one('res.company', string='Company', related='payslip_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='payslip_id.currency_id')

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount * (line.rate / 100.0)
