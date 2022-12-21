from odoo import fields, models


class ElectricalSiteRef(models.Model):
    _name = 'electrical.site.ref'
    _rec_name = 'name'
    _description = 'Electrical Site Reference'

    name = fields.Char()
