# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MechanicalReport(models.TransientModel):
    _name = "mechanical.report.wizard"
    _description = "Mechanical Report"

    start_date = fields.Date(string="Start Date", default=fields.Date.context_today, required=True)
    end_date = fields.Date(string="End Date", required=True)

    def print_mechanical_report(self):
        start_date = self.start_date
        end_date = self.end_date
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("End date must be greater than start date")
            data = {
                'start_date': start_date,
                'end_date': end_date,
            }
        return self.env.ref('mechanical_services.mechanical_operation_monthly').report_action(self, data=data)
