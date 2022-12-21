# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MechCertificateReport(models.TransientModel):
    _name = "mech.certificate.report"
    _description = "Mechanical Certificate Report"

    start_date = fields.Date(string="Start Date", default=fields.Date.context_today, required=True)
    end_date = fields.Date(string="End Date", required=True)
    customer_id = fields.Many2many('res.partner', string='Customer')

    def print_certificate_report(self):
        data = {}
        start_date = self.start_date
        end_date = self.end_date
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("End date must be greater than start date")
            data = {
                'start_date': start_date,
                'end_date': end_date,
                'customer_id': self.customer_id.ids
            }
        return self.env.ref('mechanical_services.report_completion_certificate').report_action(self, data=data)
