"""Electrical Configuration"""
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    electrical_journal_id = fields.Many2one('account.journal', 'Electrical Journal')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        electrical_journal_id = params.get_param('electrical_journal_id', default=False)
        res.update(
            electrical_journal_id=int(electrical_journal_id),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("electrical_journal_id", self.electrical_journal_id.id)
