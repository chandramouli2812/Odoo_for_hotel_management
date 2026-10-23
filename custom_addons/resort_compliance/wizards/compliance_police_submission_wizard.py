# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CompliancePoliceSubmissionWizard(models.TransientModel):
    _name = 'compliance.police.submission.wizard'
    _description = 'Police Report Batch Submission Wizard'

    report_ids = fields.Many2many('compliance.guest.report', string='Police Reports')
    authority_name = fields.Char(string='Police Authority / Station', required=True, default='Local Police Station')
    submission_date = fields.Date(string='Submission Date', required=True, default=fields.Date.today)
    submission_mode = fields.Selection([
        ('online', 'Online Police Portal / C-Form'),
        ('physical', 'Physical Submission at Police Station'),
        ('email', 'Official Police Email Intimation'),
        ('dispatch', 'Dispatch / Courier'),
    ], string='Submission Mode', default='online', required=True)
    submission_ref = fields.Char(string='Acknowledgement / Reference Number')
    mark_acknowledged = fields.Boolean(string='Mark Immediately Acknowledged', default=False)
    submission_slip = fields.Binary(string='Upload Acknowledgement Receipt / Stamp')
    submission_slip_filename = fields.Char(string='Receipt Filename')
    remarks = fields.Text(string='Submission Notes')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['report_ids'] = [(6, 0, active_ids)]
        return res

    def action_confirm_submission(self):
        self.ensure_one()
        if not self.report_ids:
            raise UserError(_("No police reports selected for submission."))

        vals = {
            'authority_name': self.authority_name,
            'submission_date': self.submission_date,
            'submission_mode': self.submission_mode,
            'submitted_by_id': self.env.user.id,
            'state': 'acknowledged' if (self.mark_acknowledged and self.submission_ref) else 'submitted',
        }
        if self.submission_ref:
            vals['submission_ref'] = self.submission_ref

        self.report_ids.write(vals)

        if self.submission_slip:
            for rep in self.report_ids:
                self.env['ir.attachment'].create({
                    'name': self.submission_slip_filename or f"Police_Ack_{rep.name}.pdf",
                    'datas': self.submission_slip,
                    'res_model': 'compliance.guest.report',
                    'res_id': rep.id,
                })

        return {'type': 'ir.actions.act_window_close'}
