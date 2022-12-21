# -*- coding: utf-8 -*-
from odoo import api, models, _


class ServiceMonthlyReport(models.AbstractModel):
    _name = 'report.generator_service_maintenance.monthly_service_report_doc'
    _description = 'Generator service report'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        start_date = data['start_date']
        end_date = data['end_date']
        query = """
                select DISTINCT(pp.engine_fsd_number) as fsd_number,
                string_agg(TO_CHAR(gs.service_date, 'DD/MM/YYYY'), ', ') as service_dates,
                count(*)
                from generator_service gs
                join product_product pp
                on pp.id = gs.service_generator_id
                where '%s' <= gs.service_date and gs.service_date <= '%s'
                group by pp.engine_fsd_number""" % (start_date, end_date)
        self._cr.execute(query)
        result = self._cr.dictfetchall()
        return {
            'doc_ids': docids,
            'data': data,
            'start_date': start_date,
            'end_date': end_date,
            'docs': result,
        }
