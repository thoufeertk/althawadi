"""Workshop workshop details"""
from odoo import fields, models


class WorkshopDetails(models.Model):
    _name = 'workshop.details'
    _rec_name = 'name'

    name = fields.Char(string="Details")
    description = fields.Text(string="Description")
