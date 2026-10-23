# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class CategoriesDict(object):
    """Allows categories.BASIC, categories.ALW etc. in salary rule expressions."""
    def __init__(self):
        self._categories = {}

    def __getattr__(self, name):
        return self._categories.get(name, 0.0)

    def __getitem__(self, name):
        return self._categories.get(name, 0.0)

    def add(self, category_code, amount):
        current = self._categories.get(category_code, 0.0)
        self._categories[category_code] = current + amount


class RulesDict(dict):
    """Allows rules.BASIC or rules['BASIC'] in rule expressions."""
    def __getattr__(self, name):
        return self.get(name, 0.0)


class MockContract(object):
    """Fallback contract when an employee has no formal contract document."""
    def __init__(self, employee, wage, struct):
        self.employee_id = employee
        self.wage = wage or 0.0
        self.struct_id = struct


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _description = 'Pay Slip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Payslip Name', required=True, default=lambda self: _('New'), tracking=True)
    number = fields.Char('Reference Number', readonly=True, copy=False, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_employee_meta', store=True, readonly=False)
    job_id = fields.Many2one('hr.job', string='Job Position', compute='_compute_employee_meta', store=True, readonly=False)
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account', compute='_compute_employee_meta', store=True, readonly=False)

    contract_id = fields.Many2one('hr.contract', string='Contract', tracking=True)
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', required=True, tracking=True)
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Batch / Pay Run', ondelete='cascade', copy=False)

    date_from = fields.Date('Date From', required=True, default=lambda self: date.today().replace(day=1), tracking=True)
    date_to = fields.Date(
        'Date To',
        required=True,
        default=lambda self: (date.today().replace(day=1) + relativedelta(months=1)) - timedelta(days=1),
        tracking=True
    )

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    # Financial Totals
    wage = fields.Monetary('Monthly Basic Wage', compute='_compute_wage_amount', store=True, readonly=False, tracking=True)
    basic_wage = fields.Monetary('Basic Pay', compute='_compute_totals', store=True)
    gross_wage = fields.Monetary('Gross Salary', compute='_compute_totals', store=True, tracking=True)
    total_deductions = fields.Monetary('Total Deductions', compute='_compute_totals', store=True)
    net_wage = fields.Monetary('Net Salary', compute='_compute_totals', store=True, tracking=True)

    worked_days_line_ids = fields.One2many('hr.payslip.worked_days', 'payslip_id', string='Worked Days', copy=True)
    line_ids = fields.One2many('hr.payslip.line', 'payslip_id', string='Salary Computation Lines', copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Computed'),
        ('done', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False)

    # Payment details
    payment_date = fields.Date('Disbursement Date', copy=False)
    payment_method = fields.Selection([
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ], string='Payment Method', default='bank', copy=False)
    payment_reference = fields.Char('Payment Reference / UTR', copy=False)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))], copy=False)
    move_id = fields.Many2one('account.move', string='Accounting Entry', readonly=True, copy=False)

    note = fields.Text('Internal Notes')

    @api.depends('employee_id')
    def _compute_employee_meta(self):
        for slip in self:
            if slip.employee_id:
                slip.department_id = getattr(slip.employee_id, 'department_id', False)
                slip.job_id = getattr(slip.employee_id, 'job_id', False)
                # Find bank account
                partner = slip.employee_id.work_contact_id or getattr(slip.employee_id, 'address_home_id', False)
                bank_acc = False
                if partner and hasattr(partner, 'bank_ids') and partner.bank_ids:
                    bank_acc = partner.bank_ids[0].id
                slip.bank_account_id = bank_acc
            else:
                slip.department_id = False
                slip.job_id = False
                slip.bank_account_id = False

    @api.depends('contract_id', 'contract_id.wage', 'employee_id')
    def _compute_wage_amount(self):
        for slip in self:
            if slip.contract_id and slip.contract_id.wage:
                slip.wage = slip.contract_id.wage
            elif slip.employee_id and hasattr(slip.employee_id, 'wage') and slip.employee_id.wage:
                slip.wage = slip.employee_id.wage
            elif not slip.wage:
                slip.wage = 0.0

    @api.depends('line_ids.total', 'line_ids.category_id.code', 'line_ids.code')
    def _compute_totals(self):
        for slip in self:
            basic = sum(l.total for l in slip.line_ids if l.category_id and l.category_id.code == 'BASIC')
            gross_line = slip.line_ids.filtered(lambda l: l.code == 'GROSS' or (l.category_id and l.category_id.code == 'GROSS'))
            if gross_line:
                gross = gross_line[0].total
            else:
                gross = sum(l.total for l in slip.line_ids if l.category_id and l.category_id.code in ('BASIC', 'ALW'))

            deductions = sum(l.total for l in slip.line_ids if l.category_id and l.category_id.code == 'DED')
            net_line = slip.line_ids.filtered(lambda l: l.code == 'NET' or (l.category_id and l.category_id.code == 'NET'))
            if net_line:
                net = net_line[0].total
            else:
                net = gross - deductions

            slip.basic_wage = basic
            slip.gross_wage = gross
            slip.total_deductions = deductions
            slip.net_wage = net

    @api.onchange('employee_id', 'date_from', 'date_to')
    def _onchange_employee_dates(self):
        if not self.employee_id:
            return

        # 1. Look for active contract
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'open'),
        ], limit=1)

        if contract:
            self.contract_id = contract.id
            self.struct_id = contract.struct_id.id
            self.wage = contract.wage
        else:
            # Fallback: check if structure is on structure_type or default structure
            default_struct = self.env.ref('custom_payroll.structure_base_monthly', raise_if_not_found=False)
            if not default_struct:
                default_struct = self.env['hr.payroll.structure'].search([], limit=1)
            if default_struct:
                self.struct_id = default_struct.id
            if hasattr(self.employee_id, 'wage') and self.employee_id.wage:
                self.wage = self.employee_id.wage

        # 2. Update default name
        if self.date_from:
            period_str = self.date_from.strftime('%B %Y')
            self.name = _("Salary Slip - %s - %s") % (self.employee_id.name, period_str)

        # 3. Populate worked days
        self._populate_worked_days()

    def _populate_worked_days(self):
        """Calculates working days and leaves for the period."""
        self.ensure_one()
        if not self.date_from or not self.date_to:
            return

        total_calendar_days = (self.date_to - self.date_from).days + 1
        unpaid_days = 0.0

        # Check for unpaid leaves if hr.holidays is available
        if 'hr.leave' in self.env:
            try:
                unpaid_leaves = self.env['hr.leave'].search([
                    ('employee_id', '=', self.employee_id.id),
                    ('state', '=', 'validate'),
                    ('date_from', '<=', self.date_to),
                    ('date_to', '>=', self.date_from),
                    ('holiday_status_id.unpaid', '=', True),
                ])
                unpaid_days = sum(l.number_of_days for l in unpaid_leaves)
            except Exception:
                unpaid_days = 0.0

        worked_days = max(0.0, total_calendar_days - unpaid_days)

        lines = [(5, 0, 0)]
        lines.append((0, 0, {
            'name': _("Normal Working Days"),
            'code': 'WORK100',
            'sequence': 1,
            'number_of_days': worked_days,
            'number_of_hours': worked_days * 8.0,
        }))

        if unpaid_days > 0:
            lines.append((0, 0, {
                'name': _("Unpaid Leaves"),
                'code': 'UNPAID',
                'sequence': 2,
                'number_of_days': unpaid_days,
                'number_of_hours': unpaid_days * 8.0,
            }))

        self.worked_days_line_ids = lines

    def action_compute_sheet(self):
        """Computes all salary lines based on the assigned structure and rules."""
        for slip in self:
            if not slip.struct_id:
                raise UserError(_("Please assign a Salary Structure to payslip '%s' before computing.") % slip.name)

            if not slip.worked_days_line_ids:
                slip._populate_worked_days()

            # Active contract or mock contract
            contract = slip.contract_id
            if not contract:
                contract = MockContract(slip.employee_id, slip.wage, slip.struct_id)

            # Execution context
            categories = CategoriesDict()
            rules = RulesDict()
            worked_days = {wd.code: wd for wd in slip.worked_days_line_ids}

            localdict = {
                'payslip': slip,
                'employee': slip.employee_id,
                'contract': contract,
                'categories': categories,
                'rules': rules,
                'worked_days': worked_days,
                'min': min,
                'max': max,
                'round': round,
                'abs': abs,
                'sum': sum,
                'float': float,
                'int': int,
                'result': 0.0,
            }

            # Fetch ordered rules
            salary_rules = slip.struct_id.get_all_rules()
            slip_lines = []

            for rule in salary_rules:
                # 1. Condition Evaluation
                condition_ok = True
                if rule.condition_select == 'python':
                    try:
                        safe_eval(rule.condition_python or 'result = True', context=localdict, mode='exec')
                        condition_ok = bool(localdict.get('result', True))
                    except Exception as e:
                        _logger.warning("Error evaluating condition for rule %s: %s", rule.code, e)
                        condition_ok = False

                if not condition_ok:
                    continue

                # 2. Amount Calculation
                amount = 0.0
                if rule.amount_select == 'fix':
                    amount = rule.amount_fix
                elif rule.amount_select == 'percentage':
                    base_val = 0.0
                    try:
                        base_val = safe_eval(rule.amount_percentage_base or 'contract.wage', context=localdict)
                    except Exception as e:
                        _logger.warning("Error calculating percentage base for rule %s: %s", rule.code, e)
                        base_val = contract.wage or 0.0
                    amount = float(base_val) * (rule.amount_percentage / 100.0)
                elif rule.amount_select == 'code':
                    try:
                        localdict['result'] = 0.0
                        safe_eval(rule.amount_python_compute or 'result = 0.0', context=localdict, mode='exec')
                        amount = float(localdict.get('result', 0.0))
                    except Exception as e:
                        _logger.error("Error computing code for rule %s: %s", rule.code, e)
                        amount = 0.0

                amount = round(amount, 2)

                # Append to line items
                slip_lines.append((0, 0, {
                    'name': rule.name,
                    'code': rule.code,
                    'salary_rule_id': rule.id,
                    'category_id': rule.category_id.id,
                    'sequence': rule.sequence,
                    'quantity': 1.0,
                    'rate': 100.0,
                    'amount': amount,
                    'appears_on_payslip': rule.appears_on_payslip,
                }))

                # Update context
                rules[rule.code] = amount
                categories.add(rule.category_id.code, amount)

            slip.line_ids = [(5, 0, 0)] + slip_lines
            slip.state = 'verify'
        return True

    def action_payslip_done(self):
        """Confirms the payslip and assigns a reference number."""
        for slip in self:
            if not slip.number:
                slip.number = self.env['ir.sequence'].next_by_code('hr.payslip') or _('New')
            slip.state = 'done'
        return True

    def action_register_payment(self):
        """Launches the payment registration wizard."""
        self.ensure_one()
        return {
            'name': _("Register Salary Payment"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payslip_ids': [(4, self.id)],
                'default_amount_total': self.net_wage,
            }
        }

    def action_payslip_paid(self):
        """Marks the payslip as paid."""
        self.write({
            'state': 'paid',
            'payment_date': self.payment_date or fields.Date.today(),
        })

    def action_payslip_cancel(self):
        self.write({'state': 'cancel'})

    def action_payslip_draft(self):
        self.write({'state': 'draft'})

    def action_print_payslip(self):
        return self.env.ref('custom_payroll.action_report_payslip').report_action(self)
