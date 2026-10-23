# -*- coding: utf-8 -*-
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _description = 'Payslip Batches'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char('Batch Name', required=True, tracking=True)
    date_start = fields.Date('Date From', required=True, default=lambda self: date.today().replace(day=1), tracking=True)
    date_end = fields.Date(
        'Date To',
        required=True,
        default=lambda self: (date.today().replace(day=1) + relativedelta(months=1)) - timedelta(days=1),
        tracking=True
    )
    struct_id = fields.Many2one('hr.payroll.structure', string='Default Salary Structure')
    slip_ids = fields.One2many('hr.payslip', 'payslip_run_id', string='Payslips')
    payslip_count = fields.Integer('Payslips Count', compute='_compute_payslip_count')
    total_net_wage = fields.Monetary('Total Net Salary', compute='_compute_batch_totals', currency_field='currency_id')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Done'),
        ('paid', 'Paid'),
    ], string='Status', default='draft', tracking=True, copy=False)

    @api.depends('slip_ids')
    def _compute_payslip_count(self):
        for run in self:
            run.payslip_count = len(run.slip_ids)

    @api.depends('slip_ids.net_wage')
    def _compute_batch_totals(self):
        for run in self:
            run.total_net_wage = sum(slip.net_wage for slip in run.slip_ids)

    def action_generate_payslips(self):
        """Opens the employee selector wizard to mass-create payslips."""
        self.ensure_one()
        return {
            'name': _("Generate Payslips for Batch"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.employees',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payslip_run_id': self.id,
                'default_struct_id': self.struct_id.id if self.struct_id else False,
            }
        }

    def action_compute_all(self):
        """Computes all payslips in the batch."""
        for run in self:
            draft_slips = run.slip_ids.filtered(lambda s: s.state in ('draft', 'verify'))
            if not draft_slips:
                raise UserError(_("No draft payslips to compute in this batch."))
            draft_slips.action_compute_sheet()
        return True

    def action_validate_all(self):
        """Validates/confirms all payslips in the batch."""
        for run in self:
            run.slip_ids.filtered(lambda s: s.state in ('draft', 'verify')).action_payslip_done()
            run.write({'state': 'close'})
        return True

    def action_paid_all(self):
        """Opens payment registration wizard for all payslips in this batch."""
        self.ensure_one()
        unpaid_slips = self.slip_ids.filtered(lambda s: s.state == 'done')
        if not unpaid_slips:
            raise UserError(_("There are no confirmed payslips ready for payment in this batch."))
        return {
            'name': _("Register Batch Salary Payment"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payslip_ids': [(6, 0, unpaid_slips.ids)],
                'default_amount_total': sum(s.net_wage for s in unpaid_slips),
            }
        }

    def action_view_payslips(self):
        self.ensure_one()
        return {
            'name': _("Payslips for %s") % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'list,kanban,form',
            'domain': [('payslip_run_id', '=', self.id)],
            'context': {'default_payslip_run_id': self.id},
        }

    def action_draft(self):
        self.write({'state': 'draft'})
