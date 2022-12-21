# -*- coding: utf-8 -*-

from odoo import api, models, _


class ServiceMonthlyReport(models.AbstractModel):
    _name = 'report.mechanical_services.monthly_mechanical_report'
    _description = 'Mechanical Operation Report'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        start_date = data['start_date']
        end_date = data['end_date']
        query = """select mwo.name as work_order_ref,mwo.work_order_date as work_order_date,
        rp.name as customer_name 
        from mechanical_work_order mwo
        join res_partner rp
        on rp.id = mwo.work_customer_id
        where '%s' <= mwo.work_order_date and ewo.work_order_date <= '%s'""" % (start_date, end_date)
        self._cr.execute(query)
        result = self._cr.dictfetchall()
        return {
            'doc_ids': docids,
            'data': data,
            'start_date': start_date,
            'end_date': end_date,
            'docs': result,
        }
