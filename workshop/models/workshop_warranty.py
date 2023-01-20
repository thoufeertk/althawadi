"""Workshop warranty"""
from odoo import fields, models


class WorkshopWarranty(models.Model):
    _name = 'workshop.warranty'
    _rec_name = 'name'

    name = fields.Char(string="Warranty")
    description = fields.Text(string="Description")
