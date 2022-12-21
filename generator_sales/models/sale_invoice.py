import datetime
from datetime import date
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for order in sale_orders:
            service = self.env['generator.service'].search([('gen_sale_order_id', '=', order.id)])
            if service:
                service.state = 'invoice'
                service_quotation_id = self.env['service.quotation'].search([('reference', '=', service.id)])
                if not service_quotation_id:
                    amc_ids = self.env['annual.maintenance.contract'].search(
                        [('contract_partner_id.id', '=', service.service_customer.id),
                         ('state', '=', 'running')])
                    for amc_id in amc_ids:
                        amc_id.contract_amount = amc_id.contract_amount - order.amount_total

        return res

