# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MechCompletionCertificate(models.Model):
    _name = 'mech.completion.certificate'
    _rec_name = 'name'
    _order = 'id desc'
    _description = 'Mechanical Completion Certificate'

    name = fields.Char()
    enquiry_date = fields.Date(string="Enquiry Date")
    enquiry_customer_id = fields.Many2one('res.partner', string='Customer Name',
                                       required=True)
    enquiry_customer_address = fields.Char(string="Address",
                                        related="enquiry_customer_id.contact_address_complete")
    work_site_ref = fields.Many2many('mechanical.site.ref',string="Site Reference")
    work_project_id = fields.Many2one('project.project', string="Project Name")
    completion_time = fields.Char(string="Completion Time")
    payment_term_id = fields.Many2one('account.payment.term',
                                      string='Payment Terms')
    quotation_id = fields.Many2one('mechanical.quotation',
                                   string="Quotation Reference")
    mechanical_work_scope_line_ids = fields.One2many('mech.work.scope.line',
                                                     'mechanical_work_id')
    mechanical_work_spare_line_ids = fields.One2many('stock.move',
                                                     'mechanical_order_move_id')
    mechanical_order_picking_id = fields.Many2one('stock.picking',
                                                  string='Related Picking')
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related="company_id.currency_id",
                                  string="Currency", readonly=True)
    # warranty = fields.Datetime(string="Warranty", default=fields.Datetime.now())
    amount_untaxed = fields.Float(string='Untaxed Amount')
    amount_tax = fields.Float(string='Tax Amount')
    amount_subtotal = fields.Float(string='Subtotal')
    enquiry_mechanical_scope_ids = fields.One2many(
        'mechanical.scope.line', 'enquiry_id')
    enquiry_spare_parts_ids = fields.One2many('mech.spare.parts.line',
                                              'enquiry_parts_id')
    work_order_id = fields.Many2one('mechanical.work.order',
                                           string='Work Order Reference')

    @api.model
    def create(self, vals):
        """Here create function is override for generating sequence for the completion.certificate"""
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'mech.completion.certificate')
        return super(MechCompletionCertificate, self).create(vals)


class MechanicalScope(models.Model):
    _name = 'mechanical.scope.line'
    _description = 'Mechanical Scope line'

    enquiry_id = fields.Many2one('mech.completion.certificate')
    enquiry_scope_id = fields.Many2one('product.product',
                                       string='Mechanical Scope',
                                       domain=[('is_mechanical', '=', True)])
    enquiry_scope_code = fields.Char(string='Item code',
                                     related='enquiry_scope_id.mechanical_item_code')
    enquiry_scope_description = fields.Char(string='Item description',
                                            related='enquiry_scope_id.mechanical_item_description')
    enquiry_scope_qty = fields.Float(string='Quantity', default=1.0)
    enquiry_scope_price = fields.Float(string='Amount',
                                       related='enquiry_scope_id.list_price')
    enquiry_tax = fields.Many2many('account.tax', string='VAT')
    enquiry_tax_amount = fields.Float(string='VAT Amount')
    enquiry_subtotal = fields.Float(string='Subtotal')
    enquiry_total = fields.Float(string='Total')


class SparePartsLine(models.Model):
    _name = 'mech.spare.parts.line'
    _description = 'Mech Spare Parts'

    enquiry_parts_id = fields.Many2one('mech.completion.certificate')
    enquiry_spare_parts_id = fields.Many2one('product.product',
                                             string='Product',
                                             domain=[
                                                 ('is_mechanical', '=', False)])
    enquiry_spare_parts_qty = fields.Char(string='Quantity', default=1.0)
    enquiry_spare_parts_unit_price = fields.Float(string='Unit Price')
