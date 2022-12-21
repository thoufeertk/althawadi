from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    workshop_stock_location = fields.Many2one(
        'stock.location', "Workshop Stock Location",
        domain="[('usage', '=', 'inventory'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
         default = lambda self: self.env.ref(
        'project_data.location_workshop').id)

