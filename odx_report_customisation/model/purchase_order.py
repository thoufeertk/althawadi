from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    with_header = fields.Boolean(default=False, string="Print with header")

    delivery_to = fields.Char(string="Delivery to")
    rev_no = fields.Char(string="Rev No.")
    rev_date = fields.Date(string="Rev Date")
    delivery_terms = fields.Char(string="Delivery Terms")



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount_amount = fields.Float(string="Discount Amount", compute="compute_discount_amount")

    @api.onchange('price_subtotal')
    def compute_discount_amount(self):
        for rec in self:
            dis = (rec.product_qty * rec.price_unit) * rec.discount / 100
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", dis)
            rec.discount_amount = dis
