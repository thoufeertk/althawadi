from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ServiceReport(models.TransientModel):
    _name = "service.report"
    _description = "Service History"

    start_date = fields.Date(string="Start Date", default=fields.Date.context_today, required=True)
    end_date = fields.Date(string="End Date", required=True)

    def print_pdf(self):
        start_date = self.start_date
        end_date = self.end_date
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("End date must be greater than start date")
            data = {
                'start_date': start_date,
                'end_date': end_date,
            }
        return self.env.ref('generator_service_maintenance.generator_service_monthly').report_action(self, data=data)
