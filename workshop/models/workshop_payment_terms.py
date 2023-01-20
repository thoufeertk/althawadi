"""Workshop Payment Terms"""
from odoo import fields, models


class WorkshopPaymentTerms(models.Model):
    _name = 'workshop.payment.terms'
    _rec_name = 'name'

    name = fields.Char(string="Payment Terms")
    description = fields.Text(string="Description")
