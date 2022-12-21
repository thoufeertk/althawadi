from datetime import date, timedelta

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    m_work_order = fields.Many2one('mechanical.work.order', string='Mechanical Work Order')
    is_m_sale = fields.Boolean()

    @api.onchange('order_line')
    def onchange_order_line(self):
        res = super(SaleOrder, self).onchange_order_line()
        current_date = date.today()
        work_order_ids = self.env['mechanical.work.order'].search(
            [('work_customer_id', '=', self.partner_id.id)], order='work_order_date DESC',
            limit=1)
        warranty_products = []
        for lines in self.order_line:
            if work_order_ids:
                for order_lines in work_order_ids.mechanical_work_scope_line_ids:
                    warranty_products.append(order_lines.mechanical_work_scope_id.id)
                    if lines.product_id.id in warranty_products:
                        warranty_date = work_order_ids.work_order_date + timedelta(days=work_order_ids.warranty_days)
                        if warranty_date < current_date:
                            lines.mech_warranty_status = 'no'
                        elif warranty_date >= current_date:
                            lines.mech_warranty_status = 'yes'
                    else:
                        lines.mech_warranty_status = 'no'
            else:
                lines.mech_warranty_status = 'no'
            if lines.mech_warranty_status == 'yes':
                lines.update({'price_unit': 0})
            else:
                lines.update({'price_unit': lines.price_unit})
        return res

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

    mech_warranty_status = fields.Selection(
        [('no', 'No'),
         ('yes', 'Yes'),
         ], string='Warranty')
