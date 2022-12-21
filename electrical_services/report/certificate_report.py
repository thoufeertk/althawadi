# -*- coding: utf-8 -*-

from odoo import api, models


class CertificateMonthlyReport(models.AbstractModel):
    _name = 'report.electrical_services.certificate_report_document'
    _description = 'Completion Certificate Report'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        start_date = data['start_date']
        end_date = data['end_date']
        customer_ids = data['customer_id']
        query = """SELECT cc.name as certificate_no,cc.completion_time,cc.enquiry_date,p.name as enquiry_customer_id from completion_certificate cc
        inner join res_partner p on cc.enquiry_customer_id = p.id
        WHERE """
        if start_date and end_date and customer_ids:
            if len(customer_ids) == 1:
                customer_ids = str(tuple(customer_ids)).replace(",", "")
            else:
                customer_ids = tuple(customer_ids)
            query += """enquiry_date >= '%s' and enquiry_date <= '%s' and enquiry_customer_id in %s""" %(start_date, end_date, customer_ids)
        else:
            query += """enquiry_date >= '%s' and enquiry_date <= '%s'""" %(start_date,end_date)
        self._cr.execute(query)
        result = self._cr.dictfetchall()
        return {
            'doc_ids': docids,
            'data': data,
            'start_date': start_date,
            'end_date': end_date,
            'customer_ids': customer_ids,
            'docs': result,
        }
