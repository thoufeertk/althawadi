# -*- coding: utf-8 -*-
from odoo import api, models


class ServiceMonthlyReport(models.AbstractModel):
    _name = 'report.generator_service_maintenance.report_service_completion'
    _description = 'Generator Service Completion'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        order_lines = []
        total_amount = 0
        service_completion_id = self.env['service.completion'].browse(docids)
        start_date = service_completion_id.start_date
        end_date = service_completion_id.end_date
        customer = service_completion_id.partner_id
        for sale_orders in service_completion_id.sale_order_ids:
            total_amount += sale_orders.sale_order_id.amount_total
            for line in sale_orders.sale_order_id.order_line:
                order_lines.append(line)
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_amount': total_amount,
            'customer': customer,
            'order_lines': order_lines,
        }
