from odoo import api, models, fields


class WorkshopQuotation(models.Model):
    _inherit = 'workshop.quotation'

    # odx_testing = fields.Html(string='Testing & Inspection', help='Write here all about Testing and Inspection', )
    odx_testing = fields.Many2one('workshop.testing.inspection', string="Testing & Inspection")
    odx_testing_description = fields.Text(related='odx_testing.description', string="Description")
    # odx_extend_of_quote = fields.Html(string='Extend of Quote')
    odx_extend_of_quote = fields.Many2one('workshop.extend.quotes', string="Extend Of Quotes")
    odx_extend_of_quote_description = fields.Text(related='odx_extend_of_quote.description', string="Description")
    # odx_terms_and_condition = fields.Html("Terms and Condition")
    odx_terms_and_condition = fields.Many2one('workshop.delivery', string="Delivery")
    odx_terms_and_condition_description = fields.Text(related='odx_terms_and_condition.description', string="Description")
    odx_gate_pass_no = fields.Char(string="Gate Pass No.")
    odx_sales_man = fields.Many2one('res.users', string="Sales Person")
    # odx_warranty = fields.Char(string="Warranty")
    odx_warranty = fields.Many2one('workshop.warranty', string="Warranty")
    odx_warranty_description = fields.Text(related='odx_warranty.description', string="Description")
    odx_payment_term = fields.Many2one('workshop.payment.terms', string="Payment Term")
    odx_payment_term_description = fields.Text(related='odx_payment_term.description', string="Description")
    odx_attention_id = fields.Many2one('res.partner', string="Attention")

    odx_header = fields.Boolean(string="With Header")

    # For tax line by line showing
    def tax_group(self):
        tax_list = []
        tax_name_list = []
        for rec in self.work_quotation_line_ids:
            if rec.display_type != 'line_section':
                for tax in rec.tax_id:
                    if rec.price_subtotal:
                        tax_amount = ((rec.price_subtotal * tax.amount)/100)
                    else:
                        tax_amount = 0
                    if tax_list:
                        for i in tax_list:
                            if tax.tax_group_id.name in tax_name_list:
                                if i['tax'] == tax.tax_group_id.name:
                                    i.update({
                                        'tax_amount': i['tax_amount']+tax_amount
                                    })
                            else:
                                tax_name_list.append(tax.tax_group_id.name)
                                tax_dict = {
                                    'tax': tax.tax_group_id.name,
                                    'name': tax.name,
                                    'tax_amount': tax_amount
                                }
                                tax_list.append(tax_dict)
                                break
                    else:
                        tax_name_list.append(tax.tax_group_id.name)
                        tax_dict = {
                                    'tax': tax.tax_group_id.name,
                                    'name': tax.name,
                                    'tax_amount': tax_amount
                                }
                        tax_list.append(tax_dict)
        return tax_list


class ResUsers(models.Model):
    _inherit = 'res.users'
    odx_sales_id = fields.Char(string="Sales ID")

# class WorkshopQuotationLine(models.Model):
#     _inherit = 'work.quotation.line'
#
#     date_of_supply = fields.Date('Date of Supply')
#     delivery_ref = fields.Char('Delivery Ref')
