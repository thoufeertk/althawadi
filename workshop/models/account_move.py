# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    pending_delivery_note = fields.Many2many('delivery.note', string="Pending Delivery Notes")

    def action_post(self):
        for pending_note in self.pending_delivery_note:
            pending_note.state = 'invoiced'
            pending_note.job_reference.state = 'invoiced'
        return super(AccountMove, self).action_post()


class SaleInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        res = super(SaleInvoice, self).create_invoices()
        sales = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for sale in sales:
            if sale.workshop_delivery_note:
                invoice = self.env['account.move'].search([('invoice_origin', '=', sale.name)], order='id desc',
                                                          limit=1)
                if invoice:
                    invoice.invoice_line_ids.update({
                        'date_of_supply': sale.workshop_delivery_note.delivery_note_date,
                        'delivery_ref': sale.workshop_delivery_note.delivery_note_no
                    })
                sale.workshop_delivery_note.state = 'invoiced'
                sale.workshop_delivery_note.job_reference.state = 'invoiced'
                contract = sale.workshop_delivery_note.job_reference.initial_inspection.contract_id
                if contract:
                    contract.contract_amount = contract.contract_amount - sale.amount_total
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    workshop_delivery_note = fields.Many2one('delivery.note')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    item_code = fields.Char(string="Item Code", store=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.item_code = self.product_id.default_code
