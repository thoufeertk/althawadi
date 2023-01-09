from odoo import models, fields, api
from odoo.exceptions import UserError


class ContributionReport(models.AbstractModel):
    _name = "report.workshop.pending_list_pdf_report"
    _description = 'Workshop Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        query = """SELECT a.name """
        if data['pending_operations'] == 'pending_enquiries':
            query += """,b.date_enquiry, b.enquiry_number from res_partner as a,enquiry_register as b WHERE 
            b.customer_name = a.id and state='pending' and  b.date_enquiry between %s and %s """

        elif data['pending_operations'] == 'pending_quotations':
            query += """  ,c.quote_date, c.name from res_partner as a,workshop_quotation as c WHERE c.customer_name = a.id and
            state='pending' and c.quote_date between %s and %s"""

        elif data['pending_operations'] == 'pending_workorders':
            query += """ ,d.order_date,d.name from res_partner as a,workshop_order as d WHERE d.customer_name = a.id and 
            state='pending' and d.order_date between %s and %s"""

        elif data['pending_operations'] == 'pending_delivery_notes':
            query += """ ,f.delivery_note_date,f.delivery_note_no from res_partner as a,delivery_note as f WHERE 
            f.customer_name = a.id and f.state='pending' and f.delivery_note_date between %s and %s"""

        else:
            raise UserError("Please select any operation")
        filters = data['start_date'], data['end_date']
        self._cr.execute(query, filters)
        record = self._cr.dictfetchall()
        return {
            'docs': record,
            'start_date': data['start_date'],
            'end_date': data['end_date']
        }
