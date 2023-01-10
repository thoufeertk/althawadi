from odoo import models, fields
from odoo.exceptions import ValidationError


class WorkshopReport(models.TransientModel):
    _name = "workshop.wizard"
    _description = 'Workshop Report Wizard'

    pending_operations = fields.Selection([('pending_enquiries', 'Pending Enquiries'),
                                           ('pending_quotations', 'Pending Quotations'),
                                           ('pending_workorders', 'Pending Workorders'),
                                           ('pending_delivery_notes', 'Pending Deliverynotes')],
                                          string='Pending Operations')

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    def print_pdf(self):
        if self.start_date > self.end_date:
            raise ValidationError('Start Date must be less than End Date')
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'pending_operations': self.pending_operations,
        }
        return self.env.ref('workshop.workshop_pending_list_report').report_action(self, data=data)
