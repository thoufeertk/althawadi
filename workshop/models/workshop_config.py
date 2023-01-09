"""Workshop Configuration"""
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # workshop_journal_id = fields.Many2one('account.journal', string='Workshop Journal')
    contract_workshop_date = fields.Char(string="Workshop Contract Days")
    contract_workshop_amount = fields.Char(string="Workshop Contract Amount")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        # workshop_journal_id = params.get_param('workshop_journal_id', default=False)
        contract_workshop_date = params.get_param('contract_workshop_date', default='10')
        contract_workshop_amount = params.get_param('contract_workshop_amount', default='2500')
        res.update(
            # workshop_journal_id=int(workshop_journal_id),
            contract_workshop_date=contract_workshop_date,
            contract_workshop_amount=contract_workshop_amount,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # self.env['ir.config_parameter'].sudo().set_param("workshop_journal_id", self.workshop_journal_id.id)
        self.env['ir.config_parameter'].sudo().set_param("contract_workshop_date", self.contract_workshop_date)
        self.env['ir.config_parameter'].sudo().set_param("contract_workshop_amount",
                                                         self.contract_workshop_amount)
