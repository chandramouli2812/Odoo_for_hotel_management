# -*- coding: utf-8 -*-
from odoo import fields, models


class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _description = 'Salary Rule'
    _order = 'sequence, id'

    name = fields.Char('Rule Name', required=True, translate=True)
    code = fields.Char('Code', required=True, help="Unique identifier for rule calculations (e.g. BASIC, HRA, PF)")
    sequence = fields.Integer('Sequence', default=5, help="Order of computation. Rules with lower sequence compute first.")
    category_id = fields.Many2one('hr.salary.rule.category', string='Category', required=True)
    active = fields.Boolean('Active', default=True)
    appears_on_payslip = fields.Boolean('Appears on Payslip', default=True, help="If checked, this rule will show on the employee's printed payslip.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Condition
    condition_select = fields.Selection([
        ('none', 'Always True'),
        ('python', 'Python Expression'),
    ], string='Condition Based on', default='none', required=True)
    condition_python = fields.Text('Python Condition', default='result = True', help="Expression that sets 'result = True' or 'result = False'")

    # Computation
    amount_select = fields.Selection([
        ('fix', 'Fixed Amount'),
        ('percentage', 'Percentage (%)'),
        ('code', 'Python Code'),
    ], string='Amount Type', default='code', required=True)
    amount_fix = fields.Float('Fixed Amount', digits='Product Price', default=0.0)
    amount_percentage = fields.Float('Percentage (%)', digits='Payroll Rate', default=0.0)
    amount_percentage_base = fields.Char('Percentage based on', default='contract.wage', help="Field name or python expression to calculate percentage from.")
    amount_python_compute = fields.Text('Python Code', default='result = contract.wage * 0.5', help="Calculation logic. Must set 'result'.")

    note = fields.Text('Description / Notes')
