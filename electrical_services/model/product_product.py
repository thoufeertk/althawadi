# -*- coding: utf-8 -*-
from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.template'

    is_electrical = fields.Boolean(string='Is Electrical')
    # electrical_item_code = fields.Char(string='Electrical Item Code')
    electrical_item_description = fields.Char(string='Item Description')
    electrical_spare_parts_ids = fields.One2many('electrical.parts.line', 'electrical_product_id', copy=True)
    scope_type = fields.Selection([
        ('supply_only', 'Supply Only'),
        ('supply_fix', 'Supply & Fix'),
        ('removal_only', 'Removal Only'),
        ('fixing_only', 'Fixing Only'),
        ('cleaning', 'Cleaning'),
    ])


class ProductLine(models.Model):
    _name = "electrical.parts.line"
    _description = 'Electrical Spare Parts'

    electrical_product_id = fields.Many2one('product.product')
    spare_product_id = fields.Many2one('product.product', string="Product",
                                       domain=[('is_electrical', '=', False), ('type', '=', 'product')])
    spare_product_price = fields.Float(string="Unit Price", related='spare_product_id.lst_price')
    spare_product_quantity = fields.Float(string="Quantity", default=1.0)
