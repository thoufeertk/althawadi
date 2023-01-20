"""Workshop Testing and Inspections"""
from odoo import fields, models


class WorkshopTestingInspection(models.Model):
    _name = 'workshop.testing.inspection'
    _rec_name = 'name'

    name = fields.Char(string="Testing And Inspection")
    description = fields.Text(string="Description")
