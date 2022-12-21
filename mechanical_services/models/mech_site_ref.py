from odoo import fields, models


class MechanicalSiteRef(models.Model):
    _name = 'mechanical.site.ref'
    _rec_name = 'name'
    _description = 'Mechanical Site Reference'

    name = fields.Char()
