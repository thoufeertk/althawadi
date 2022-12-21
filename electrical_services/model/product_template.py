# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    electrical_stock_location = fields.Many2one(
        'stock.location', "Electrical Location",
        domain="[('usage', '=', 'production'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        default=lambda self: self.env.ref(
            'project_data.location_electrical').id)
