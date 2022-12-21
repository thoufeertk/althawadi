# -*- coding: utf-8 -*-
#######################################################################################
#
#    WANTECH Innovation Technology Ltd
#
#    Copyright (C) WANTECH Innovation Technology Ltd(<http://www.wantech.com.hk>).
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
########################################################################################

from odoo import api, fields, models, SUPERUSER_ID, _


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrderInherit, self)._create_invoices(grouped=grouped, final=final)
        for order in self:
            service = self.env['generator.service'].sudo().search([('gen_sale_order_id', '=', order.id)])
            if service and service[0]:
                if service.amc_contract_id and service.amc_contract_id.cust_purchase_order_no:
                    res.write({'invoice_origin': service.amc_contract_id.cust_purchase_order_no})
        return res
