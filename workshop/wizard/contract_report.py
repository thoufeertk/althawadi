from odoo import models, fields
from odoo.exceptions import ValidationError


class ContractReport(models.TransientModel):
    _name = "contract.wizard"
    _description = 'Contract Report Wizard'

    expiry = fields.Selection([('expires_within', 'Expires Within'),
                                           ('amc_amount', 'Contract Amount'),
                                           ],default='expires_within')

    days = fields.Integer(string="Day(s)", required=True)
    amc_amount = fields.Float(string='AMC amount', required=True)

    def print_pdf(self):
        data = {
            'days': self.days,
            'amount': self.amc_amount,
            'expiry': self.expiry
        }

        return self.env.ref('workshop.contract_report').report_action(self, data=data)
