# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CompletionCertificate(models.Model):
    _name = 'completion.certificate'
    _rec_name = 'name'
    _order = 'id desc'
    _description = 'Completion Certificate'

    name = fields.Char()
    enquiry_date = fields.Date(string="Enquiry Date")
    enquiry_customer_id = fields.Many2one('res.partner', string='Customer Name',
                                       required=True)
    enquiry_customer_address = fields.Char(string="Address",
                                        related="enquiry_customer_id.contact_address_complete")
    work_site_ref = fields.Many2many('electrical.site.ref',string="Site Reference")
    work_project_id = fields.Many2one('project.project', string="Project Name")
    completion_time = fields.Char(string="Completion Time")
    payment_term_id = fields.Many2one('account.payment.term',
                                      string='Payment Terms')
    quotation_id = fields.Many2one('electrical.quotation',
                                   string="Quotation Reference")
    electrical_work_scope_line_ids = fields.One2many('work.scope.line',
                                                     'electrical_work_id')
    electrical_work_spare_line_ids = fields.One2many('stock.move',
                                                     'electrical_order_move_id')
    electrical_order_picking_id = fields.Many2one('stock.picking',
                                                  string='Related Picking')
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related="company_id.currency_id",
                                  string="Currency", readonly=True)
    amount_untaxed = fields.Float(string='Untaxed Amount')
    amount_tax = fields.Float(string='Tax Amount')
    amount_subtotal = fields.Float(string='Subtotal')
    enquiry_electrical_scope_ids = fields.One2many(
        'electrical.scope.line', 'enquiry_id')
    enquiry_spare_parts_ids = fields.One2many('spare.parts.line',
                                              'enquiry_parts_id')
    work_order_id = fields.Many2one('electrical.work.order',
                                           string='Work Order Reference')

    @api.model
    def create(self, vals):
        """Here create function is override for generating sequence for the completion.certificate"""
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'completion.certificate')
        return super(CompletionCertificate, self).create(vals)


class ElectricalScope(models.Model):
    _name = 'electrical.scope.line'
    _description = 'Electrical Scope line'

    enquiry_id = fields.Many2one('completion.certificate')
    enquiry_scope_id = fields.Many2one('product.product',
                                       string='Electrical Scope',
                                       domain=[('is_electrical', '=', True)])
    enquiry_scope_code = fields.Char(string='Item code',
                                     related='enquiry_scope_id.default_code')
    enquiry_scope_description = fields.Char(string='Item description',
                                            related='enquiry_scope_id.electrical_item_description')
    enquiry_scope_qty = fields.Float(string='Quantity', default=1.0)
    enquiry_scope_price = fields.Float(string='Amount',
                                       related='enquiry_scope_id.lst_price')
    enquiry_tax = fields.Many2many('account.tax', string='VAT')
    enquiry_tax_amount = fields.Float(string='VAT Amount')
    enquiry_subtotal = fields.Float(string='Subtotal')
    enquiry_total = fields.Float(string='Total')
    warranty_status = fields.Selection(
        [('no', 'No'),
         ('yes', 'Yes'),
         ], string='Warranty', default='no')


class SparePartsLine(models.Model):
    _name = 'spare.parts.line'
    _description = 'Spare Parts'

    enquiry_parts_id = fields.Many2one('completion.certificate')
    enquiry_spare_parts_id = fields.Many2one('product.product',
                                             string='Product',
                                             domain=[
                                                 ('is_electrical', '=', False)])
    enquiry_spare_parts_qty = fields.Char(string='Quantity', default=1.0)
    enquiry_spare_parts_unit_price = fields.Float(string='Unit Price')
