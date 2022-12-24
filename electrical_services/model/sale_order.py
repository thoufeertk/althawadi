from datetime import date, timedelta

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    e_work_order = fields.Many2one('electrical.work.order', string='Electrical Work Order')
    is_e_sale = fields.Boolean()

    @api.onchange('order_line')
    def onchange_order_line(self):
        print('innnnn')
        current_date = date.today()
        work_order_ids = self.env['electrical.work.order'].search(
            [('work_customer_id', '=', self.partner_id.id)], order='work_order_date DESC',
            limit=1)
        warranty_products = []
        for lines in self.order_line:
            if work_order_ids:
                for order_lines in work_order_ids.electrical_work_scope_line_ids:
                    warranty_products.append(order_lines.electrical_work_scope_id.id)
                    if lines.product_id.id in warranty_products:
                        warranty_date = work_order_ids.work_order_date + timedelta(days=work_order_ids.warranty_days)
                        if warranty_date < current_date:
                            lines.elec_warranty_status = 'no'
                        elif warranty_date >= current_date:
                            lines.elec_warranty_status = 'yes'
                    else:
                        lines.elec_warranty_status = 'no'
            else:
                lines.elec_warranty_status = 'no'
            if lines.elec_warranty_status == 'yes':
                lines.update({'price_unit': 0})
            else:
                lines.update({'price_unit': lines.price_unit})

    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     if args is None:
    #         args = []
    #     domain = args + ['|', ('client_order_ref', operator, name), ('name', operator, name)]
    #     model_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
    #     return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid))

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = []
        domain = args + ['|', ('client_order_ref', operator, name), ('name', operator, name)]
        model_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        # return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super(SaleOrder, self)._search(domain, limit=limit, access_rights_uid=name_get_uid)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    elec_warranty_status = fields.Selection(
        [('no', 'No'),
         ('yes', 'Yes'),
         ], string='Warranty')


class SaleInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        res = super(SaleInvoice, self).create_invoices()
        sale = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if sale.e_work_order:
            sale.e_work_order.state = 'invoiced'
            if sale.e_work_order.enquiry_id.contract_id:
                sale.e_work_order.enquiry_id.contract_id.amc_contract_amount = sale.e_work_order.enquiry_id.contract_id.amc_contract_amount - sale.amount_total
        return res
