"""Workshop Scope of Work"""
from odoo import fields, models


class WorkshopScopeOfWork(models.Model):
    _name = 'workshop.scopeofwork'
    _rec_name = 'name'

    name = fields.Char(string="Scope of Work")
    description = fields.Text(string="Description")
