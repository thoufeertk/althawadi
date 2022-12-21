# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    vat_account_no = fields.Char(related='partner_id.vat',help='Partner Vat Account Number')
    company_vat_no = fields.Char(related='company_id.partner_id.vat',help='Company Vat Account Number')
    street = fields.Char('Street',related='company_id.partner_id.street')
    street2 = fields.Char('Street2',related='company_id.partner_id.street2')
    zip = fields.Char('Zip', related='company_id.partner_id.zip')
    city = fields.Char('City',related='company_id.partner_id.city')
    state_id = fields.Many2one("res.country.state", related='company_id.partner_id.state_id',string='State')
    country_id = fields.Many2one('res.country', related='company_id.partner_id.country_id',string='Country')
    order_date = fields.Datetime(string='Order Date')


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    date_of_supply = fields.Date('Date of Supply')
    delivery_ref = fields.Char('Delivery Ref')
    ordinal_number = fields.Integer(compute='_compute_get_number', store=True)

    @api.depends('sequence', 'move_id', 'ordinal_number')
    def _compute_get_number(self):
        """This compute function is for creating the ordinal number for the
        account move line."""
        for rec in self:
            rec.ordinal_number = False
            ordinal_number = 1
            for line in rec.move_id.invoice_line_ids:
                line.ordinal_number = ordinal_number
                ordinal_number += 1


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        """Pass app category to invoice"""
        res = super(SaleOrderInherit, self)._prepare_invoice()
        res.update({
            'order_date': self.date_order
        })
        return res






