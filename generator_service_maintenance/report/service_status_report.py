# -*- coding: utf-8 -*-
from odoo import api, models, _


class ServiceStatusReport(models.AbstractModel):
    _name = 'report.generator_service_maintenance.status_template'
    _description = 'Generator Service Status Report'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        start_date = data['start_date']
        end_date = data['end_date']
        query = """
                select gs.id,pp.engine_fsd_number as fsd_number,
                gs.state, gs.service_estimated_cost as cost
                from generator_service gs
                join product_product pp
                on pp.id = gs.service_generator_id 
                where '%s' <= gs.service_date and gs.service_date <= '%s'
                order by gs.service_date""" % (start_date, end_date)

        self._cr.execute(query)
        result = self._cr.dictfetchall()
        company_id = self.env.company
        return {
            'doc_ids': docids,
            'data': data,
            'start_date': start_date,
            'end_date': end_date,
            'docs': result,
            'company_id': company_id
        }
