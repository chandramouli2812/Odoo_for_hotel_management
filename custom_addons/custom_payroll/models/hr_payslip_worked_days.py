# -*- coding: utf-8 -*-
from odoo import fields, models


class HrPayslipWorkedDays(models.Model):
    _name = 'hr.payslip.worked_days'
    _description = 'Payslip Worked Days'
    _order = 'payslip_id, sequence'

    name = fields.Char('Description', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer('Sequence', default=10)
    code = fields.Char('Code', required=True, default='WORK100', help="Code used in salary rules: e.g. WORK100, UNPAID")
    number_of_days = fields.Float('Number of Days', default=30.0)
    number_of_hours = fields.Float('Number of Hours', default=240.0)
    contract_id = fields.Many2one('hr.contract', string='Contract', related='payslip_id.contract_id', store=True)
