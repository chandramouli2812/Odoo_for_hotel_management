# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HotelHousekeepingTask(models.Model):
    _name = 'hotel.housekeeping.task'
    _description = 'Hotel Housekeeping Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc, priority desc, id desc'

    name = fields.Char(string='Task No', copy=False, readonly=True, default=lambda self: _('New'))
    room_id = fields.Many2one('hotel.room', string='Room', required=True, tracking=True)
    property_id = fields.Many2one('hotel.property', related='room_id.property_id', string='Property', store=True)

    task_type = fields.Selection([
        ('checkout_clean', 'Checkout Turnaround Cleaning'),
        ('stayover_clean', 'Daily Stayover Cleaning'),
        ('deep_clean', 'Deep Cleaning & Sanitization'),
        ('inspection', 'Supervisor Inspection'),
        ('turndown', 'Evening Turndown Service'),
        ('maintenance_fix', 'Minor Room Maintenance Check'),
    ], string='Task Type', default='checkout_clean', required=True, tracking=True)

    assigned_to_id = fields.Many2one('hr.employee', string='Assigned Housekeeper', tracking=True)
    scheduled_date = fields.Date(string='Scheduled Date', default=fields.Date.context_today, required=True, tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Standard'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1')

    state = fields.Selection([
        ('draft', 'Pending'),
        ('in_progress', 'Cleaning In Progress'),
        ('done', 'Cleaned'),
        ('inspected', 'Inspected & Approved'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    notes = fields.Text(string='Checklist / Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hotel.housekeeping.task') or _('New')
        return super().create(vals_list)

    def action_start(self):
        for task in self:
            task.write({'state': 'in_progress'})
            task.room_id.write({'housekeeping_status': 'cleaning'})

    def action_done(self):
        for task in self:
            task.write({'state': 'done'})
            task.room_id.write({'housekeeping_status': 'clean'})

    def action_inspect(self):
        for task in self:
            task.write({'state': 'inspected'})
            task.room_id.write({'housekeeping_status': 'inspected'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
