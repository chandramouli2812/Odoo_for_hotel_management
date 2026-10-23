# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    _name = 'hr.contract'
    _description = 'Employee Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char('Contract Reference', required=True, default=lambda self: _('New'), tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_employee_details', store=True, readonly=False)
    job_id = fields.Many2one('hr.job', string='Job Position', compute='_compute_employee_details', store=True, readonly=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    date_start = fields.Date('Start Date', required=True, default=fields.Date.today, tracking=True)
    date_end = fields.Date('End Date', tracking=True)
    trial_date_end = fields.Date('Trial Period End Date')

    wage = fields.Monetary('Monthly Basic Wage', required=True, tracking=True, help="Gross or base monthly salary used for payroll calculations.")
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='open', tracking=True, copy=False)

    notes = fields.Html('Terms and Notes')

    @api.depends('employee_id')
    def _compute_employee_details(self):
        for contract in self:
            if contract.employee_id:
                contract.department_id = getattr(contract.employee_id, 'department_id', False)
                contract.job_id = getattr(contract.employee_id, 'job_id', False)
                if not contract.wage and hasattr(contract.employee_id, 'wage') and contract.employee_id.wage:
                    contract.wage = contract.employee_id.wage

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.contract') or _('New')
        return super().create(vals_list)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for contract in self:
            if contract.date_end and contract.date_end < contract.date_start:
                raise ValidationError(_("Contract End Date cannot be earlier than the Start Date."))

    def action_set_running(self):
        self.write({'state': 'open'})

    def action_set_expired(self):
        self.write({'state': 'close'})

    def action_set_cancel(self):
        self.write({'state': 'cancel'})

    def action_set_draft(self):
        self.write({'state': 'draft'})
