# -*- coding: utf-8 -*-
from odoo import fields, models


class OtherCharges(models.Model):
    _name = 'other.charges'
    _description = 'Other Charges'

    initial_inspection_id = fields.Many2one('initial.inspection')
    charge_description = fields.Char(string='Description')
    charge_cost = fields.Float(string='Cost')
