# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    contract_ids = fields.One2many('hr.contract', 'employee_id', string='Contracts')
    payslip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips')
    payslip_count = fields.Integer('Payslips Count', compute='_compute_payroll_counts')
    contract_count = fields.Integer('Contracts Count', compute='_compute_payroll_counts')

    @api.depends('payslip_ids', 'contract_ids')
    def _compute_payroll_counts(self):
        for emp in self:
            emp.payslip_count = len(emp.payslip_ids)
            emp.contract_count = len(emp.contract_ids)

    def action_view_payslips(self):
        self.ensure_one()
        return {
            'name': _("Payslips - %s") % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'list,kanban,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': _("Contracts - %s") % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'hr.contract',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
