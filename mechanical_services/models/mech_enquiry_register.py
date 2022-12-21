# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning


class MechanicalEnquiryRegister(models.Model):
    _name = 'mechanical.enquiry.register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Mechanical Enquiry Register'

    name = fields.Char(default='New')
    enquiry_date = fields.Date(string="Date", default=fields.Date.today())
    enquiry_customer_id = fields.Many2one('res.partner', string='Customer Name', required=True)
    enquiry_customer_address = fields.Char(related="enquiry_customer_id.contact_address_complete", string="Address",
                                           store=True, index=True)
    enquiry_site_reference = fields.Many2many('mechanical.site.ref', string="Site Reference")
    enquiry_project_id = fields.Many2one('project.project', string="Project Name",
                                         default=lambda self: self.env.ref(
                                             'project_data.project_project_mechanical').id)
    mechanical_project = fields.Char(string='Project')
    contract_id = fields.Many2one('mech.amc.contract')
    completion_time = fields.Char(string="Completion Time")
    # warranty = fields.Datetime(string="Warranty", default=fields.Datetime.now())
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    state = fields.Selection([
        ('draft', 'Enquiry'),
        ('submit', 'Submitted'),
        ('waiting', 'Waiting For Approval'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('quotation', 'Quotation'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    enquiry_mechanical_scope_ids = fields.One2many('enquiry.mechanical.scope.line', 'enquiry_id')
    enquiry_mechanical_parts_ids = fields.One2many('enquiry.mechanical.parts.line', 'enquiry_parts_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related="company_id.currency_id",
                                  string="Currency", readonly=True)
    check_amc = fields.Boolean()
    amount_total = fields.Float(compute='_compute_amount', string='Total')
    amount_tax = fields.Float(compute='_compute_amount', string='Taxes')
    amount_untaxed = fields.Float(compute='_compute_amount',
                                  string='Untaxed Amount')
    work_order_count = fields.Integer(compute='_compute_work_order_count')
    work_quotation_count = fields.Integer(compute='_compute_work_order_count')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Reference', domain=[('is_m_sale', '=', True)])

    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        self.enquiry_customer_id = self.sale_order_id.partner_id.id
        self.payment_term_id = self.payment_term_id.id
        scope_list = [(5, 0, 0)]
        for order_line in self.sale_order_id.order_line:
            vals = {
                'enquiry_scope_id': order_line.product_id.id,
                'enquiry_scope_code': order_line.product_id.mechanical_item_code,
                'enquiry_scope_description': order_line.product_id.mechanical_item_description,
                'enquiry_scope_qty': order_line.product_uom_qty,
                'enquiry_scope_price': order_line.price_unit,
                'enquiry_tax': order_line.tax_id.ids,
                'enquiry_subtotal': order_line.price_subtotal,
                'enquiry_total': order_line.price_total,
            }
            scope_list.append((0, 0, vals))
            self.update({'enquiry_mechanical_scope_ids': scope_list})

    def _compute_work_order_count(self):
        for enquiry_id in self:
            enquiry_id.work_order_count = enquiry_id.env['mechanical.work.order'].search_count(
                [('enquiry_id', '=', enquiry_id.id)]) or 0
            enquiry_id.work_quotation_count = enquiry_id.env['mechanical.quotation'].search_count(
                [('enquiry_id', '=', enquiry_id.id)]) or 0

    @api.depends('enquiry_mechanical_scope_ids.enquiry_total')
    def _compute_amount(self):
        for scope in self:
            amount_untaxed = amount_tax = 0.0
            for line in scope.enquiry_mechanical_scope_ids:
                amount_untaxed += line.enquiry_subtotal
                amount_tax += line.enquiry_tax_amount
            scope.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax
            })

    @api.onchange('enquiry_customer_id')
    @api.depends('enquiry_customer_id')
    def _onchange_enquiry_customer_id(self):
        amc_contract_id = self.env['mech.amc.contract'].search(
            [('amc_customer_id', '=', self.enquiry_customer_id.id), ('state', '=', 'running')], limit=1)
        if amc_contract_id:
            self.check_amc = True
            self.contract_id = amc_contract_id.id
        else:
            self.check_amc = False
            self.contract_id = False

    def submit_enquiry(self):
        if self.check_amc:
            self.state = 'waiting'
        else:
            self.state = 'submit'
        self.name = self.env['ir.sequence'].next_by_code('mechanical.enquiry.register')

    @api.onchange('enquiry_mechanical_scope_ids')
    @api.depends('enquiry_mechanical_scope_ids')
    def _onchange_enquiry_mechanical_scope_ids(self):
        """ Get values from mechanical spare parts and assign to Bill of material """
        spare_parts_list = [(5, 0, 0)]
        for spare_parts_ids in self.enquiry_mechanical_scope_ids:
            if spare_parts_ids:
                for spare_parts_id in spare_parts_ids:
                    for spares in spare_parts_id.enquiry_scope_id.mechanical_spare_parts_ids:
                        spare_parts_vals = {
                            'enquiry_spare_parts_id': spares.spare_product_id.id,
                            'enquiry_spare_parts_qty': spares.spare_product_quantity,
                            'enquiry_spare_parts_unit_price': spares.spare_product_price,
                        }
                        if self.contract_id:
                            for spare in self.contract_id.amc_mechanical_parts_ids:
                                if spare.amc_parts_id.id == spares.spare_product_id.id:
                                    spare_parts_vals.update({
                                        'enquiry_spare_parts_unit_price': spare.amc_parts_unit_price
                                    })
                        spare_parts_list.append((0, 0, spare_parts_vals))
                        self.update({'enquiry_mechanical_parts_ids': spare_parts_list})

    def add_attachments(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'mechanical.enquiry.register'),
                         ('res_id', '=', self.id)]
        res['context'] = {'default_res_model': 'mechanical.enquiry.register',
                          'default_res_model_name': 'Mechanical Enquiry Register',
                          'default_res_id': self.id}
        return res

    def create_quotation(self):
        """ Create quotation from enquiry """
        mechanical_quotation = self.env["mechanical.quotation"]
        vals = {
            'mechanical_quotation_date': fields.Date.today(),
            'mechanical_customer_id': self.enquiry_customer_id.id,
            'mechanical_customer_address': self.enquiry_customer_address,
            'mechanical_site_ref': self.enquiry_site_reference.ids,
            'mechanical_project_id': self.enquiry_project_id.id,
            'completion_time': self.completion_time,
            # 'warranty': self.warranty,
            'enquiry_id': self.id,
            'sale_order_id': self.sale_order_id.id,
            'payment_term_id': self.payment_term_id.id,
            'state': 'draft',
        }
        quotation_id = mechanical_quotation.create(vals)
        if quotation_id:
            if self.enquiry_mechanical_scope_ids:
                for scope in self.enquiry_mechanical_scope_ids:
                    scope_list = []
                    vals = (0, 0, {
                        'quotation_scope_id': scope.enquiry_scope_id.id,
                        'quotation_scope_code': scope.enquiry_scope_code,
                        'quotation_scope_description': scope.enquiry_scope_description,
                        'quotation_scope_qty': scope.enquiry_scope_qty,
                        'quotation_scope_price': scope.enquiry_scope_price,
                        'quotation_scope_tax': scope.enquiry_tax.ids,
                        'quotation_scope_subtotal': scope.enquiry_subtotal,
                        'quotation_scope_total': scope.enquiry_total,
                        'quotation_scope_tax_amount': scope.enquiry_tax_amount,
                    })
                    scope_list.append(vals)
                    quotation_id.update({'quotation_scope_line_ids': scope_list})
            if self.enquiry_mechanical_parts_ids:
                for parts in self.enquiry_mechanical_parts_ids:
                    spare_parts_list = []
                    vals = (0, 0, {
                        'quotation_spare_parts_id': parts.enquiry_spare_parts_id.id,
                        'quotation_spare_parts_qty': parts.enquiry_spare_parts_qty,
                        'quotation_spare_parts_unit_price': parts.enquiry_spare_parts_unit_price,
                    })
                    spare_parts_list.append(vals)
                    quotation_id.update({'quotation_spare_line_ids': spare_parts_list})
        self.write({'state': 'quotation'})
        view_id = self.env.ref('mechanical_services.view_mechanical_quotation_form').id
        return {
            'view_mode': 'form',
            'res_model': 'mechanical.quotation',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': quotation_id.id
        }

    def work_order_approve(self):
        """This is the reject function which send the corresponding record to the
        approved list"""
        if self.enquiry_mechanical_scope_ids and self.enquiry_mechanical_parts_ids:
            self.sudo().write({
                'state': 'approve'
            })
        else:
            self.sudo().write({
                'state': 'approve'
            })
            # raise Warning(_("Please fill the Scope/Spare lines"))

    def work_order_reject(self):
        """This is the reject function which send the corresponding record to the
        rejected list"""
        self.sudo().write({
            'state': 'reject'
        })

    def create_work_order(self):
        picking_type_id = self.env.ref('stock.picking_type_internal')
        location_id = picking_type_id.default_location_src_id.id
        destination_id = picking_type_id.default_location_dest_id.id
        if location_id and destination_id:
            picking_vals = {
                'partner_id': self.enquiry_customer_id.id,
                'picking_type_id': picking_type_id.id,
                'location_id': location_id,
                'location_dest_id': destination_id,
            }
            picking_id = self.env['stock.picking'].sudo().create(picking_vals)

            work_order = self.env['mechanical.work.order'].create({
                'work_order_date': self.enquiry_date,
                'work_customer_id': self.enquiry_customer_id.id,
                'work_customer_address': self.enquiry_customer_address,
                'work_site_ref': self.enquiry_site_reference.ids,
                'work_project_id': self.enquiry_project_id.id,
                'mechanical_order_picking_id': picking_id.id,
                'completion_time': self.completion_time,
                'payment_term_id': self.payment_term_id.id,
                'enquiry_id': self.id,
                'sale_order_reference': self.sale_order_id.id,
                'mechanical_work_scope_line_ids': [(0, 0, {
                    'mechanical_work_scope_id': enquiry_mechanical_scope_id.enquiry_scope_id.id,
                    'mechanical_work_scope_code': enquiry_mechanical_scope_id.enquiry_scope_code,
                    'mechanical_work_scope_description': enquiry_mechanical_scope_id.enquiry_scope_description,
                    'mechanical_work_qty': enquiry_mechanical_scope_id.enquiry_scope_qty,
                    'mechanical_work_scope_price': enquiry_mechanical_scope_id.enquiry_scope_price,
                    'mechanical_work_tax': enquiry_mechanical_scope_id.enquiry_tax.ids,
                    'mechanical_work_tax_amount': enquiry_mechanical_scope_id.enquiry_tax_amount,
                    'mechanical_work_subtotal': enquiry_mechanical_scope_id.enquiry_subtotal,
                    'mechanical_work_total': enquiry_mechanical_scope_id.enquiry_total,
                }) for enquiry_mechanical_scope_id in self.enquiry_mechanical_scope_ids],
                'mechanical_work_spare_line_ids': [(0, 0, {
                    'picking_type_id': picking_type_id.id,
                    'picking_id': picking_id.id,
                    'name': enquiry_mechanical_parts_ids.enquiry_spare_parts_id.name,
                    'product_id': enquiry_mechanical_parts_ids.enquiry_spare_parts_id.id,
                    'product_uom_qty': enquiry_mechanical_parts_ids.enquiry_spare_parts_qty,
                    'price_unit': enquiry_mechanical_parts_ids.enquiry_spare_parts_unit_price,
                    'location_id': picking_type_id.default_location_src_id.id,
                    'product_uom': enquiry_mechanical_parts_ids.enquiry_spare_parts_id.uom_id.id,
                    'location_dest_id': enquiry_mechanical_parts_ids.enquiry_spare_parts_id.mechanical_stock_location.id,
                }) for enquiry_mechanical_parts_ids in self.enquiry_mechanical_parts_ids],
            })
            return {
                'name': 'Work Order',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mechanical.work.order',
                'res_id': work_order.id,
                'target': 'current'
            }

    def button_mechanical_quotation(self):
        """This is the function of the smart button which redirect to the invoice related to the current service"""
        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mechanical.quotation',
            'domain': [('enquiry_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    def button_mechanical_work_order(self):
        """This is the function of the smart button which redirect to the invoice related to the current service"""
        return {
            'name': 'Work Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mechanical.work.order',
            'domain': [('enquiry_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }


class EnquiryScopeLine(models.Model):
    _name = 'enquiry.mechanical.scope.line'
    _description = 'Enquiry Mechanical Scope'

    enquiry_id = fields.Many2one('mechanical.enquiry.register')
    enquiry_scope_id = fields.Many2one('product.product', string='Mechanical Scope',
                                       domain=[('is_mechanical', '=', True)])
    enquiry_scope_code = fields.Char(string='Item code', related='enquiry_scope_id.mechanical_item_code')
    enquiry_scope_description = fields.Char(string='Item description',
                                            related='enquiry_scope_id.mechanical_item_description')
    enquiry_scope_qty = fields.Float(string='Quantity', default=1.0)
    enquiry_scope_price = fields.Float(string='Amount', related='enquiry_scope_id.list_price')
    enquiry_tax = fields.Many2many('account.tax', string='VAT')
    enquiry_tax_amount = fields.Float(string='VAT Amount')
    enquiry_subtotal = fields.Float(string='Subtotal')
    enquiry_total = fields.Float(string='Total', compute='_compute_enquiry_total')

    @api.depends('enquiry_scope_qty', 'enquiry_scope_price', 'enquiry_tax')
    def _compute_enquiry_total(self):
        if self.enquiry_id.contract_id:
            for mechanical_scope in self.enquiry_id.contract_id.amc_mechanical_scope_ids:
                for scope in self:
                    if mechanical_scope.amc_scope_id.id == scope.enquiry_scope_id.id:
                        scope.update(
                            {'enquiry_scope_price': mechanical_scope.amc_scope_price})
        for scope_line_id in self:
            scope_line_id.enquiry_subtotal = scope_line_id.enquiry_scope_qty * scope_line_id.enquiry_scope_price
            if scope_line_id.enquiry_tax:
                scope_line_id.enquiry_total = scope_line_id.enquiry_subtotal + (
                        (scope_line_id.enquiry_subtotal * sum(scope_line_id.enquiry_tax.mapped('amount'))) / 100)
            else:
                scope_line_id.enquiry_total = scope_line_id.enquiry_subtotal
            scope_line_id.enquiry_tax_amount = scope_line_id.enquiry_total - scope_line_id.enquiry_subtotal

    @api.onchange('enquiry_scope_id')
    def _onchange_enquiry_scope_id(self):
        for scope_id in self:
            if not scope_id.enquiry_id.enquiry_customer_id:
                warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a customer.'),
                }
                return {'warning': warning}
            else:
                scope_id.enquiry_tax = scope_id.enquiry_scope_id.taxes_id.ids


class MechanicalPartsLine(models.Model):
    _name = 'enquiry.mechanical.parts.line'
    _description = 'Enquiry Mechanical Spare Parts'

    enquiry_parts_id = fields.Many2one('mechanical.enquiry.register')
    enquiry_spare_parts_id = fields.Many2one('product.product', string='Product',
                                             domain=[('is_mechanical', '=', False)])
    enquiry_spare_parts_qty = fields.Char(string='Quantity', default=1.0)
    enquiry_spare_parts_unit_price = fields.Float(string='Unit Price')
