# -*- coding: utf-8 -*-
from odoo import fields, models, api


class HrPayrollStructure(models.Model):
    _name = 'hr.payroll.structure'
    _description = 'Salary Structure'
    _order = 'name'

    name = fields.Char('Structure Name', required=True, translate=True)
    code = fields.Char('Reference / Code', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    rule_ids = fields.Many2many(
        'hr.salary.rule',
        'hr_payroll_structure_rule_rel',
        'struct_id',
        'rule_id',
        string='Salary Rules'
    )
    rule_count = fields.Integer('Rules Count', compute='_compute_rule_count')
    note = fields.Text('Description / Policy')

    @api.depends('rule_ids')
    def _compute_rule_count(self):
        for struct in self:
            struct.rule_count = len(struct.rule_ids)

    def get_all_rules(self):
        """Returns rules ordered by sequence."""
        self.ensure_one()
        return self.rule_ids.filtered(lambda r: r.active).sorted(key=lambda r: (r.sequence, r.id))
