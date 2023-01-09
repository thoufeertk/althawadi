# -*- coding: utf-8 -*-
from odoo import fields, models


class MachineType(models.Model):
    _name = 'machine.type'
    _rec_name = 'name'
    _description = 'Machine Type'

    name = fields.Char(string='Name')
    description = fields.Text()



