# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _name = 'hr.payslip.employees'
    _description = 'Generate Payslips for Batch'

    payslip_run_id = fields.Many2one('hr.payslip.run', string='Batch / Pay Run', required=True)
    department_id = fields.Many2one('hr.department', string='Filter by Department')
    employee_ids = fields.Many2many('hr.employee', string='Select Employees')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    auto_compute = fields.Boolean('Automatically Compute Sheets', default=True, help="If checked, immediately calculates all salary lines for generated slips.")

    @api.onchange('department_id')
    def _onchange_department_id(self):
        domain = [('active', '=', True)]
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))
        employees = self.env['hr.employee'].search(domain)
        self.employee_ids = [(6, 0, employees.ids)]

    def action_select_all_employees(self):
        self.ensure_one()
        all_emps = self.env['hr.employee'].search([('active', '=', True)])
        self.employee_ids = [(6, 0, all_emps.ids)]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.employees',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def compute_sheet(self):
        self.ensure_one()
        if not self.employee_ids:
            raise UserError(_("Please select at least one employee to generate payslips."))

        run = self.payslip_run_id
        default_struct = self.struct_id or run.struct_id or self.env.ref('custom_payroll.structure_base_monthly', raise_if_not_found=False)
        if not default_struct:
            default_struct = self.env['hr.payroll.structure'].search([], limit=1)

        created_slips = self.env['hr.payslip']

        for employee in self.employee_ids:
            # Check if slip already exists in this run
            existing = run.slip_ids.filtered(lambda s: s.employee_id.id == employee.id)
            if existing:
                continue

            # Look for active contract
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'open'),
            ], limit=1)

            struct = contract.struct_id if contract and contract.struct_id else default_struct
            wage = contract.wage if contract and contract.wage else (getattr(employee, 'wage', 0.0) or 0.0)

            period_name = run.date_start.strftime('%B %Y')
            slip_vals = {
                'name': _("Salary Slip - %s - %s") % (employee.name, period_name),
                'employee_id': employee.id,
                'payslip_run_id': run.id,
                'date_from': run.date_start,
                'date_to': run.date_end,
                'contract_id': contract.id if contract else False,
                'struct_id': struct.id if struct else False,
                'wage': wage,
            }
            slip = self.env['hr.payslip'].create(slip_vals)
            slip._populate_worked_days()
            created_slips |= slip

        if self.auto_compute and created_slips:
            created_slips.action_compute_sheet()

        return {'type': 'ir.actions.act_window_close'}
