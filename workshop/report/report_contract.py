from odoo import models, api
from odoo.exceptions import UserError


class ContractReport(models.AbstractModel):
    _name = "report.workshop.contract_report"
    _description = 'Contract Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        query = """SELECT name,contract_amount,contract_start_date,
        contract_end_date """
        if data['expiry'] == 'expires_within':
            query += """from workshop_contract where contract_end_date <= (CURRENT_DATE + INTERVAL ' """ + str(data['days']) + """ day')"""
        elif data['expiry'] == 'amc_amount':
            query += """ from workshop_contract WHERE contract_amount <= """ + str(
                data['amount'])
        else:
            raise UserError("Please select any operation")
        self._cr.execute(query)
        record = self._cr.dictfetchall()
        return {
            'docs': record,
            'data': data
        }
