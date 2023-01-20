"""Workshop Extend Of Quotes"""
from odoo import fields, models


class WorkshopExtendQuotes(models.Model):
    _name = 'workshop.extend.quotes'
    _rec_name = 'name'

    name = fields.Char(string="Extend Of Quotes")
    description = fields.Text(string="Description")
