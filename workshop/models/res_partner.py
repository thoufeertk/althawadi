from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    show_price_details = fields.Boolean(string='Enable to show pricing in Delivery Note')
