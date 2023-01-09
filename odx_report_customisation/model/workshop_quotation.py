from odoo import api,models,fields

class WorkshopQuotation(models.Model):
    _inherit = 'workshop.quotation'

    odx_testing = fields.Html(string='Testing & Inspection', help='Write here all about Testing and Inspection', )
    odx_extend_of_quote = fields.Html(string='Extend of Quote')
    odx_terms_and_condition = fields.Html("Terms and Condition")
    odx_gate_pass_no = fields.Char(string="Gate Pass No.")
    odx_sales_man = fields.Many2one('res.users',string="Sales Person")
    odx_warranty = fields.Char(string="Warranty")
    odx_header = fields.Boolean(string="With Header")


class ResUsers(models.Model):
    _inherit = 'res.users'
    odx_sales_id = fields.Char(string="Sales ID")


# class WorkshopQuotationLine(models.Model):
#     _inherit = 'work.quotation.line'
#
#     date_of_supply = fields.Date('Date of Supply')
#     delivery_ref = fields.Char('Delivery Ref')