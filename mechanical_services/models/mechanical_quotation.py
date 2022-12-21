# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MechanicalQuotation(models.Model):
    _name = 'mechanical.quotation'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Mechanical Quotation'

    name = fields.Char(default=lambda self: _('New'))
    mechanical_quotation_date = fields.Date(string="Date", default=fields.Date.today())
    mechanical_customer_id = fields.Many2one('res.partner', string='Customer Name', required=True)
    mechanical_customer_address = fields.Char(string="Address",
                                              related="mechanical_customer_id.contact_address_complete")
    mechanical_site_ref = fields.Many2many('mechanical.site.ref', string="Site Reference")
    mechanical_project_id = fields.Many2one('project.project', string="Project Name")
    completion_time = fields.Char(string="Completion Time")
    # warranty = fields.Datetime(string="Warranty", default=fields.Datetime.now())
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    enquiry_id = fields.Many2one('mechanical.enquiry.register', string="Enquiry")
    quotation_scope_line_ids = fields.One2many('mech.quotation.scope.line', 'quotation_id')
    quotation_spare_line_ids = fields.One2many('mech.quotation.spare.line', 'quotation_parts_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related="company_id.currency_id",
                                  string="Currency", readonly=True)
    amount_total = fields.Float(compute='_compute_amount', string='Total')
    amount_tax = fields.Float(compute='_compute_amount', string='Taxes')
    amount_untaxed = fields.Float(compute='_compute_amount', string='Untaxed Amount')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('approved', 'Approved'),
        ('workorder', 'Work Order'),
        ('rejected', 'Rejected'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')

    work_order_count = fields.Integer(compute='_compute_work_order_count')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Reference')

    def _compute_work_order_count(self):
        for quotation_id in self:
            quotation_id.work_order_count = quotation_id.env['mechanical.work.order'].search_count(
                [('quotation_id', '=', quotation_id.id)]) or 0

    def action_print(self):
        print('Printing......')

    @api.depends('quotation_scope_line_ids.quotation_scope_total')
    def _compute_amount(self):
        for scope in self:
            amount_untaxed = amount_tax = 0.0
            for line in scope.quotation_scope_line_ids:
                amount_untaxed += line.quotation_scope_subtotal
                amount_tax += line.quotation_scope_tax_amount
            scope.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax
            })

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('mechanical.quotation') or _('New')
        return super(MechanicalQuotation, self).create(vals)

    def action_approve(self):
        """For changing the state to approved"""
        self.sudo().write({
            'state': 'approved'
        })

    def action_reject(self):
        """For Changing the state to reject"""
        self.sudo().write({
            'state': 'rejected'
        })

    def create_work_order(self):
        """Function for creating work order from the quotation"""
        picking_type_id = self.env.ref('stock.picking_type_internal')
        location_id = picking_type_id.default_location_src_id.id
        destination_id = picking_type_id.default_location_dest_id.id
        if location_id and destination_id:
            picking_vals = {
                'partner_id': self.mechanical_customer_id.id,
                'picking_type_id': picking_type_id.id,
                'location_id': location_id,
                'location_dest_id': destination_id,
            }
            picking_id = self.env['stock.picking'].sudo().create(picking_vals)

            work_order = self.env['mechanical.work.order'].create({
                'work_order_date': self.mechanical_quotation_date,
                'work_customer_id': self.mechanical_customer_id.id,
                'work_customer_address': self.mechanical_customer_address,
                'work_site_ref': self.mechanical_site_ref.ids,
                'work_project_id': self.mechanical_project_id.id,
                'mechanical_order_picking_id': picking_id.id,
                'completion_time': self.completion_time,
                # 'warranty': self.warranty,
                'payment_term_id': self.payment_term_id.id,
                'quotation_id': self.id,
                'enquiry_id': self.enquiry_id.id,
                'sale_order_reference': self.sale_order_id.id,
                'mechanical_work_scope_line_ids': [(0, 0, {
                    'mechanical_work_scope_id': scope_line_id.quotation_scope_id.id,
                    'mechanical_work_scope_code': scope_line_id.quotation_scope_code,
                    'mechanical_work_scope_description': scope_line_id.quotation_scope_description,
                    'mechanical_work_qty': scope_line_id.quotation_scope_qty,
                    'mechanical_work_scope_price': scope_line_id.quotation_scope_price,
                    'mechanical_work_tax': scope_line_id.quotation_scope_tax.ids,
                    'mechanical_work_tax_amount': scope_line_id.quotation_scope_tax_amount,
                    'mechanical_work_subtotal': scope_line_id.quotation_scope_subtotal,
                    'mechanical_work_total': scope_line_id.quotation_scope_total,
                }) for scope_line_id in self.quotation_scope_line_ids],
                'mechanical_work_spare_line_ids': [(0, 0, {
                    'picking_type_id': picking_type_id.id,
                    'picking_id': picking_id.id,
                    'name': spare_line_id.quotation_spare_parts_id.name,
                    'product_id': spare_line_id.quotation_spare_parts_id.id,
                    'product_uom_qty': spare_line_id.quotation_spare_parts_qty,
                    'price_unit': spare_line_id.quotation_spare_parts_unit_price,
                    'location_id': picking_type_id.default_location_src_id.id,
                    'product_uom': spare_line_id.quotation_spare_parts_id.uom_id.id,
                    'location_dest_id': spare_line_id.quotation_spare_parts_id.mechanical_stock_location.id,
                }) for spare_line_id in self.quotation_spare_line_ids],
            })
            return {
                'name': 'Work Order',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mechanical.work.order',
                'res_id': work_order.id,
                'target': 'current'
            }

    def action_send_mail(self):
        """Send material request details to the customer"""
        self.ensure_one()
        print('aaaaaaaa')
        ir_model_data = self.env['ir.model.data']
        try:
                template_id = ir_model_data._xmlid_lookup('mechanical_services.email_template_mechanical_quotation')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'mechanical.quotation',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def button_mechanical_work_order(self):
        """This is the function of the smart button which redirect to the invoice related to the current service"""
        return {
            'name': 'Work Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mechanical.work.order',
            'domain': [('quotation_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }


class EnquiryScopeLine(models.Model):
    _name = 'mech.quotation.scope.line'
    _description = 'Mechanical Quotation Scope'

    quotation_id = fields.Many2one('mechanical.quotation')
    quotation_scope_id = fields.Many2one('product.product', string='Mechanical Scope',
                                         domain=[('is_mechanical', '=', True)])
    quotation_scope_code = fields.Char(string='Item code')
    quotation_scope_description = fields.Char(string='Item description')
    quotation_scope_qty = fields.Float(string='Quantity', default=1.0)
    quotation_scope_price = fields.Float(string='Amount')
    quotation_scope_tax = fields.Many2many('account.tax', string='VAT')
    quotation_scope_tax_amount = fields.Float(string='VAT Amount')
    quotation_scope_subtotal = fields.Float(string='Subtotal')
    quotation_scope_total = fields.Float(string='Total')


class MechanicalPartsLine(models.Model):
    _name = 'mech.quotation.spare.line'
    _description = 'Quotation Mechanical Spare Parts'

    quotation_parts_id = fields.Many2one('mechanical.quotation')
    quotation_spare_parts_id = fields.Many2one('product.product', string='Product',
                                               domain=[('is_mechanical', '=', False)])
    quotation_spare_parts_qty = fields.Char(string='Quantity', default=1.0)
    quotation_spare_parts_unit_price = fields.Float(string='Unit Price')
