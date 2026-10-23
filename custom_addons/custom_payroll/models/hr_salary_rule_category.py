# -*- coding: utf-8 -*-
from odoo import fields, models


class HrSalaryRuleCategory(models.Model):
    _name = 'hr.salary.rule.category'
    _description = 'Salary Rule Category'
    _order = 'sequence, id'

    name = fields.Char('Category Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence', default=10)
    parent_id = fields.Many2one('hr.salary.rule.category', string='Parent Category', ondelete='cascade')
    children_ids = fields.One2many('hr.salary.rule.category', 'parent_id', string='Children')
    note = fields.Text('Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
