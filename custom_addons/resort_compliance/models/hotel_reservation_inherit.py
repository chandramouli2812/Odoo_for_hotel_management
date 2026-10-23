# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    compliance_report_ids = fields.One2many(
        'compliance.guest.report',
        'reservation_id',
        string='Police Intimations'
    )
    compliance_report_count = fields.Integer(
        string='Police Reports Count',
        compute='_compute_compliance_counts'
    )

    foreign_guest_ids = fields.One2many(
        'compliance.foreign.guest',
        'reservation_id',
        string='FRRO / Form C Records'
    )
    foreign_guest_count = fields.Integer(
        string='Form C Count',
        compute='_compute_compliance_counts'
    )

    incident_ids = fields.One2many(
        'compliance.incident',
        'reservation_id',
        string='Compliance Incidents'
    )
    incident_count = fields.Integer(
        string='Incident Count',
        compute='_compute_compliance_counts'
    )

    def _compute_compliance_counts(self):
        for rec in self:
            rec.compliance_report_count = len(rec.compliance_report_ids)
            rec.foreign_guest_count = len(rec.foreign_guest_ids)
            rec.incident_count = len(rec.incident_ids)

    def action_view_police_reports(self):
        self.ensure_one()
        return {
            'name': _('Police Intimations & Reports'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.guest.report',
            'view_mode': 'list,form',
            'domain': [('reservation_id', '=', self.id)],
            'context': {
                'default_reservation_id': self.id,
                'default_guest_id': self.guest_id.id,
                'default_room_id': self.room_id.id,
                'default_property_id': self.property_id.id,
                'default_arrival_date': self.check_in,
                'default_departure_date': self.check_out,
            }
        }

    def action_view_foreign_reports(self):
        self.ensure_one()
        return {
            'name': _('FRRO / Form C Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.foreign.guest',
            'view_mode': 'list,form',
            'domain': [('reservation_id', '=', self.id)],
            'context': {
                'default_reservation_id': self.id,
                'default_guest_id': self.guest_id.id,
                'default_room_id': self.room_id.id,
                'default_property_id': self.property_id.id,
                'default_arrival_at_hotel': self.check_in,
                'default_expected_departure': self.check_out,
            }
        }

    def action_view_incidents(self):
        self.ensure_one()
        return {
            'name': _('Incidents & Police Cases'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.incident',
            'view_mode': 'list,form',
            'domain': [('reservation_id', '=', self.id)],
            'context': {
                'default_reservation_id': self.id,
                'default_guest_id': self.guest_id.id,
                'default_room_id': self.room_id.id,
                'default_property_id': self.property_id.id,
            }
        }

    def action_quick_create_police_intimation(self):
        self.ensure_one()
        india = self.env.ref('base.in', raise_if_not_found=False)
        is_foreign = False
        if hasattr(self.guest_id, 'nationality_id') and self.guest_id.nationality_id:
            is_foreign = bool(india and self.guest_id.nationality_id != india)

        report = self.env['compliance.guest.report'].create({
            'guest_id': self.guest_id.id,
            'reservation_id': self.id,
            'room_id': self.room_id.id if self.room_id else False,
            'property_id': self.property_id.id if self.property_id else False,
            'nationality_id': self.guest_id.nationality_id.id if hasattr(self.guest_id, 'nationality_id') and self.guest_id.nationality_id else False,
            'reporting_type': 'foreign' if is_foreign else 'arrival',
            'id_type': 'passport' if is_foreign else 'aadhaar',
            'id_number': getattr(self.guest_id, 'id_number', '') or '',
            'arrival_date': self.check_in,
            'departure_date': self.check_out,
            'accompanying_adults': max(0, self.adults - 1),
            'accompanying_children': self.children,
        })
        return {
            'name': _('Police Guest Intimation'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.guest.report',
            'res_id': report.id,
            'view_mode': 'form',
        }
