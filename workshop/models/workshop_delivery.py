"""Workshop Delivery"""
from odoo import fields, models


class WorkshopDelivery(models.Model):
    _name = 'workshop.delivery'
    _rec_name = 'name'

    name = fields.Char(string="Delivery")
    description = fields.Text(string="Description")
