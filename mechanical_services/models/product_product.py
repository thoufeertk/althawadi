# -*- coding: utf-8 -*-
from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.template'

    is_mechanical = fields.Boolean(string='Is Mechanical')
    mechanical_item_code = fields.Char(string='Mechanical Item Code')
    mechanical_item_description = fields.Char(string='Item Description')
    mechanical_spare_parts_ids = fields.One2many('mechanical.parts.line', 'mechanical_product_id', copy=True)
    type = fields.Selection(
        selection=[
            ('consu', 'Consumable'),
            ('service', 'Service'),
            ('product', 'Storable Product')
        ],

        store=True,
        readonly=True,
    )


class ProductLine(models.Model):
    _name = "mechanical.parts.line"
    _description = 'Mechanical Spare Parts'

    mechanical_product_id = fields.Many2one('product.product')
    spare_product_id = fields.Many2one('product.product', string="Product",
                                       domain=[('is_mechanical', '=', False), ('type', '=', 'product')])
    spare_product_price = fields.Float(string="Unit Price", related='spare_product_id.lst_price')
    spare_product_quantity = fields.Float(string="Quantity", default=1.0)
