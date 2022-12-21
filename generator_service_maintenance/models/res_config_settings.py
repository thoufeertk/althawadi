# -*- coding: utf-8 -*-
"""Workshop Configuration"""
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # generator_journal_id = fields.Many2one('account.journal', string='Generator Service Journal')
    contract_maintenance_date = fields.Char(string="Days")
    contract_maintenance_amount = fields.Char(string="Amount")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        # generator_journal_id = params.get_param('generator_journal_id', default=False)
        contract_maintenance_date = params.get_param('contract_maintenance_date', default='10')
        contract_maintenance_amount = params.get_param('contract_maintenance_amount', default='2500')
        res.update(
            # generator_journal_id=int(generator_journal_id),
            contract_maintenance_date=contract_maintenance_date,
            contract_maintenance_amount=contract_maintenance_amount,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # self.env['ir.config_parameter'].sudo().set_param("generator_journal_id", self.generator_journal_id.id)
        self.env['ir.config_parameter'].sudo().set_param("contract_maintenance_date", self.contract_maintenance_date)
        self.env['ir.config_parameter'].sudo().set_param("contract_maintenance_amount",
                                                         self.contract_maintenance_amount)
