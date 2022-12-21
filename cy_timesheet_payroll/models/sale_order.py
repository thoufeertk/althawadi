from odoo import models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('client_order_ref')
    def _onchange_client_order_ref(self):
        sale_order_ids = self.env['sale.order'].search([])
        for sale_order in sale_order_ids:
            if sale_order.client_order_ref == self.client_order_ref and self.client_order_ref:
                raise UserError(_('This Customer Order Reference Already Exist'))
