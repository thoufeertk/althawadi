"""Mechanical Configuration"""
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mechanical_journal_id = fields.Many2one('account.journal', 'Mechanical Journal')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        mechanical_journal_id = params.get_param('mechanical_journal_id', default=False)
        res.update(
            mechanical_journal_id=int(mechanical_journal_id),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("mechanical_journal_id", self.mechanical_journal_id.id)
