from odoo import fields, models, api


class res_company(models.Model):

    _inherit = "res.company"
    header_image = fields.Image(string="Header",  max_width=1920, max_height=1920,force_save=True)
    footer_image = fields.Image(string="Footer", force_save=True)
    stamp_image = fields.Image(string="Stamp", force_save=True)

