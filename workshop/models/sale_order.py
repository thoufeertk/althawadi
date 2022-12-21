from datetime import date, timedelta

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_w_sale = fields.Boolean()
    work_quotation_id = fields.Many2one('workshop.quotation', string="Workshop Quotation")

    @api.onchange('work_quotation_id')
    def _onchange_work_quotation_id(self):
        sale_line_ids = [(5, 0, 0)]
        for quotation_line in self.work_quotation_id.work_quotation_line_ids:
            sale_line = {
                'product_id': quotation_line.product_id.id,
                'name': quotation_line.name,
                'display_type': quotation_line.display_type,
                'product_uom_qty': quotation_line.product_uom_qty,
                'price_unit': quotation_line.price_unit,
                'product_uom': quotation_line.product_uom,
                'discount': quotation_line.discount,
                'tax_id': quotation_line.tax_id.ids,
            }
            sale_line_ids.append((0, 0, sale_line))
        self.update({
            'partner_id': self.work_quotation_id.customer_name.id,
            'order_line': sale_line_ids
        })

    @api.onchange('order_line')
    def onchange_order_line(self):
        res = super(SaleOrder, self).onchange_order_line()
        current_date = date.today()
        work_order_ids = self.env['workshop.order'].search(
            [('customer_name', '=', self.partner_id.id)], order='order_date DESC',
            limit=1)
        warranty_products = []
        for lines in self.order_line:
            if work_order_ids:
                warranty_products.append(work_order_ids.initial_inspection.machine_type.id)
                if work_order_ids.warranty_days == 0:
                    lines.work_warranty_status = 'no'
                elif lines.product_id.id in warranty_products:
                    warranty_date = work_order_ids.order_date + timedelta(days=work_order_ids.warranty_days)
                    if warranty_date < current_date:
                        lines.work_warranty_status = 'no'
                    elif warranty_date >= current_date:
                        lines.work_warranty_status = 'yes'
                else:
                    lines.work_warranty_status = 'no'
            else:
                lines.work_warranty_status = 'no'
            if lines.work_warranty_status == 'yes':
                lines.update({'price_unit': 0})
            else:
                lines.update({'price_unit': lines.price_unit})
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    work_warranty_status = fields.Selection(
        [('no', 'No'),
         ('yes', 'Yes'),
         ], string='Warranty')
