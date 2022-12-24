from datetime import datetime

from odoo import models, fields, api


class MechPoWizard(models.TransientModel):
    _name = 'mech.po.wizard'
    _description = "Create Purchase Order"

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    origin = fields.Char(string='Origin', readonly=True)
    order_line_ids = fields.One2many('mech.po.wizard.line', 'order_line_id', String="Order Line")

    def create_purchase(self):
        order_line = []
        for line_ids in self.order_line_ids:
            order_line.append((0, 0, {
                'product_id': line_ids.product_id.id,
                'name': line_ids.product_id.name,
                'product_qty': line_ids.product_uom_qty,
                'price_unit': line_ids.product_price_unit,
                'price_subtotal': line_ids.price_subtotal,
                'date_planned': datetime.today(),
                'product_uom': line_ids.product_uom.id,
            }))
        purchase_obj = self.env['purchase.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'order_line': order_line,
            'origin': self.origin
        })


class MechPoWizardLine(models.TransientModel):
    _name = 'mech.po.wizard.line'
    _description = "Create Purchase Order Line"

    order_line_id = fields.Many2one('mech.po.wizard')
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_qty = fields.Float(string='Quantity', required=True)
    product_price_unit = fields.Float(string="Unit Price", required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    price_subtotal = fields.Float(string="Subtotal")

    @api.onchange('product_uom_qty', 'product_price_unit')
    def _onchange_product_price(self):
        self.price_subtotal = self.product_price_unit * self.product_uom_qty
