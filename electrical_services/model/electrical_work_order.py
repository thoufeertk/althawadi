# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class WorkOrder(models.Model):
    _name = 'electrical.work.order'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Electrical Work Order'

    name = fields.Char(default=lambda self: _('New'))
    work_order_date = fields.Date(string="Date", default=fields.Date.today())
    work_customer_id = fields.Many2one('res.partner', string='Customer Name',
                                       required=True)
    work_customer_address = fields.Char(string="Address",
                                        related="work_customer_id.contact_address_complete")
    work_site_ref = fields.Many2many('electrical.site.ref', string="Site Reference")
    work_project_id = fields.Many2one('project.project', string="Project Name")
    completion_time = fields.Char(string="Completion Time")
    payment_term_id = fields.Many2one('account.payment.term',
                                      string='Payment Terms',
                                      related='work_customer_id.property_supplier_payment_term_id',
                                      readonly=False)
    enquiry_id = fields.Many2one('electrical.enquiry.register',
                                 string="Enquiry")
    quotation_id = fields.Many2one('electrical.quotation',
                                   string="Quotation Reference")
    electrical_technician_ids = fields.One2many('electrical.technician.line', 'work_order_id')
    state = fields.Selection([
        ('waiting_material', 'Waiting Material'),
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('finish', 'Finished'),
        ('invoiced', 'Invoiced')], string='State',
        copy=False, default='waiting_material', required=True,
        track_visibility='onchange')
    electrical_work_scope_line_ids = fields.One2many('work.scope.line',
                                                     'electrical_work_id')
    electrical_work_spare_line_ids = fields.One2many('stock.move',
                                                     'electrical_order_move_id')
    electrical_order_picking_id = fields.Many2one('stock.picking',
                                                  string='Related Picking')
    material_request_count = fields.Integer(compute='_compute_count')
    invoice_count = fields.Integer(compute='_compute_count')
    task_count = fields.Integer(compute='_compute_count')
    completion_certificate_count = fields.Integer(compute='_compute_count')
    check_task_status = fields.Boolean(string='Task Status')
    check_dead_line = fields.Boolean(compute='_compute_check_dead_line')
    sale_order_reference = fields.Many2one('sale.order', string='Sale Order Reference')
    warranty_days = fields.Integer(string='Warranty Days')

    @api.onchange('sale_order_reference')
    def _onchange_sale_order_reference(self):
        self.ensure_one()
        for word_order in self:
            word_order.sale_order_reference.e_work_order = word_order.id

    def _compute_check_dead_line(self):
        """For checking the dead-line of the task and
        changing the color of the tree view"""
        current_date = date.today()
        for work_order in self:
            project_task = work_order.env['project.task'].search([('electrical_order_id', '=', work_order.id)], limit=1)
            if project_task and project_task.date_deadline:
                if project_task.date_deadline >= current_date:
                    work_order.check_dead_line = True
                else:
                    work_order.check_dead_line = False
            else:
                work_order.check_dead_line = False

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'electrical.work.order') or _('New')
        return super(WorkOrder, self).create(vals)

    def _compute_count(self):
        for order in self:
            order.material_request_count = self.env[
                'electrical.material.request'].search_count(
                [('pending_list', '=', order.id)])
            order.task_count = self.env['project.task'].search_count(
                [('electrical_order_id', '=', order.id)])
            order.invoice_count = self.env['account.move'].search_count(
                [('electrical_work_order_id', '=', order.id)])
            order.completion_certificate_count = self.env['completion.certificate'].search_count(
                [('work_order_id', '=', order.id)])

    def action_view_material_request(self):
        """ Return the related Material Request of the Order.
        """
        return {
            'name': _('Material Request'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'electrical.material.request',
            'domain': [('pending_list', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }

    def action_view_completion_certificate(self):
        """ Return the related Material Request of the Order.
        """
        return {
            'name': _('Completion Certificate'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'completion.certificate',
            'domain': [('work_order_id', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }

    def action_view_invoice(self):
        """ Return the related Invoice of the Order.
        """
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('electrical_work_order_id', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }

    def action_view_tasks(self):
        """ Return the related Task of the Order.
        """
        return {
            'name': _('Tasks'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('electrical_order_id', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }

    def check_availability(self):
        moves = self.electrical_work_spare_line_ids.filtered(
            lambda x: x.state not in ('done', 'cancel'))._action_confirm()
        moves._action_assign()
        material_request = self.env['electrical.material.request']
        material_request_line = self.env['electrical.material.request.line']
        if any(line.state in ['confirmed', 'partially_available'] for line in
               self.electrical_work_spare_line_ids):
            if self.material_request_count == 0:
                vals = {
                    'partner_id': self.work_customer_id.id,
                    'pending_list': self.id,
                    'date': self.work_order_date,
                    'site_reference': self.work_site_ref.ids,
                    'project_id': self.work_project_id.id,
                }
                request_id = material_request.create(vals)
                material_request_line.create({
                                                 'work_spare_parts_id': material_line.product_id.id,
                                                 'work_spare_parts_qty': material_line.product_uom_qty - material_line.reserved_availability,
                                                 'work_spare_parts_unit_price': material_line.price_unit,
                                                 'material_request_id': request_id.id,
                                             } for material_line in
                                             self.electrical_work_spare_line_ids.filtered(
                                                 lambda line: line.state in [
                                                     'confirmed',
                                                     'partially_available']))
        else:
            self.write({'state': 'draft'})

    def start_work(self):
        """
        Change the related stock moves to done,create related tasks
        """
        current_date = date.today()
        dead_line = current_date + timedelta(days=int(self.completion_time))
        self.electrical_order_picking_id.origin = self.name
        self.sale_order_reference.e_work_order = self.id
        for line in self.electrical_work_spare_line_ids:
            line.electrical_order_move_id = self.id
            line.quantity_done = line.product_uom_qty
        self.electrical_order_picking_id.button_validate()
        self.electrical_order_picking_id.message_post_with_view(
            'mail.message_origin_link',
            values={'self': self.electrical_order_picking_id, 'origin': self},
            subtype_id=self.env.ref('mail.mt_note').id)
        technician_list = []
        for technician_line in self.electrical_technician_ids:
            technician_list.append(technician_line.technician_id.id)
        if not technician_list:
            raise ValidationError("Choose atleast one technician!!!")
        self.env['project.task'].create({
            'name': self.name,
            'kanban_state': 'normal',
            'project_id': self.env.ref(
                'project_data.project_project_electrical').id,
            'partner_id': self.work_customer_id.id,
            'date_deadline': dead_line,
            'electrical_order_id': self.id,
            'priority': '1',
            'date_assign': date.today(),
            'technician_ids': technician_list,
        })
        self.state = 'running'

    def finish_work(self):
        self.state = 'finish'
        if not self.check_task_status:
            raise UserError(_('Timesheets are not submitted'))

    def generate_completion_certificate(self):
        certificate = self.env['completion.certificate']
        certificate_id = certificate.create({
            'enquiry_date': self.enquiry_id.enquiry_date,
            'enquiry_customer_id': self.enquiry_id.enquiry_customer_id.id,
            'work_site_ref': self.enquiry_id.enquiry_site_reference.ids,
            'enquiry_customer_address': self.enquiry_id.enquiry_customer_address,
            'work_project_id': self.enquiry_id.enquiry_project_id.id,
            'completion_time': self.enquiry_id.completion_time,
            'payment_term_id': self.enquiry_id.payment_term_id.id,
            'work_order_id': self.id,
            'amount_untaxed': self.enquiry_id.amount_untaxed,
            'amount_tax': self.enquiry_id.amount_tax,
            'amount_subtotal': self.enquiry_id.amount_total,
            'enquiry_electrical_scope_ids': [(0, 0, {
                'enquiry_scope_id': electrical_scope.enquiry_scope_id.id,
                'enquiry_scope_code': electrical_scope.enquiry_scope_code,
                'enquiry_scope_description': electrical_scope.enquiry_scope_description,
                'enquiry_scope_qty': electrical_scope.enquiry_scope_qty,
                'enquiry_scope_price': electrical_scope.enquiry_scope_price,
                'enquiry_tax': electrical_scope.enquiry_tax,
                'enquiry_tax_amount': electrical_scope.enquiry_tax_amount,
                'enquiry_subtotal': electrical_scope.enquiry_subtotal,
                'enquiry_total': electrical_scope.enquiry_total
            })
                                             for electrical_scope in
                                             self.enquiry_id.enquiry_electrical_scope_ids],
            'enquiry_spare_parts_ids': [(0, 0, {
                'enquiry_spare_parts_id': spare_part.enquiry_spare_parts_id.id,
                'enquiry_spare_parts_qty': spare_part.enquiry_spare_parts_qty,
                'enquiry_spare_parts_unit_price': spare_part.enquiry_spare_parts_unit_price
            })
                                        for spare_part in
                                        self.enquiry_id.enquiry_electrical_parts_ids],
        })
        return {
            'name': 'Certificate',
            'type': 'ir.actions.act_window',
            'res_model': 'completion.certificate',
            'view_mode': 'form',
            'target': 'current',
            'res_id': certificate_id.id
        }

    # def create_invoice(self):
    #     current_user = self.env.uid
    #     invoice_journal = self.env['ir.config_parameter'].sudo().get_param(
    #         'electrical_journal_id') or False
    #     if not invoice_journal:
    #         raise UserError(_('Configure Journal for Electrical service from the settings'))
    #     if invoice_journal:
    #         self.ensure_one()
    #         invoice_line_list = []
    #         for work_scope_id in self.electrical_work_scope_line_ids:
    #             vals = (0, 0, {
    #                 'name': str(
    #                     work_scope_id.electrical_work_scope_id.name) + '' + str(
    #                     work_scope_id.electrical_work_scope_code),
    #                 'price_unit': work_scope_id.electrical_work_scope_price,
    #                 'account_id': work_scope_id.electrical_work_scope_id.property_account_income_id.id if work_scope_id.electrical_work_scope_id.property_account_income_id
    #                 else work_scope_id.electrical_work_scope_id.categ_id.property_account_income_categ_id.id,
    #                 'tax_ids': work_scope_id.electrical_work_tax.ids if work_scope_id.electrical_work_tax else False,
    #                 'quantity': work_scope_id.electrical_work_qty,
    #                 'price_subtotal': work_scope_id.electrical_work_subtotal,
    #                 'price_total': work_scope_id.electrical_work_total,
    #             })
    #             invoice_line_list.append(vals)
    #         invoice = self.env['account.move'].create({
    #             'type': 'out_invoice',
    #             'invoice_origin': self.name,
    #             'invoice_user_id': current_user,
    #             'narration': self.name,
    #             'electrical_work_order_id': self.id,
    #             'partner_id': self.work_customer_id.id,
    #             'currency_id': self.env.user.company_id.currency_id.id,
    #             'journal_id': int(invoice_journal),
    #             'invoice_payment_term_id': self.payment_term_id.id,
    #             'invoice_payment_ref': self.name,
    #             'invoice_line_ids': invoice_line_list
    #         })
    #         return invoice


class EnquiryScopeLine(models.Model):
    _name = 'work.scope.line'
    _description = 'Electrical Work Scope'

    electrical_work_id = fields.Many2one('electrical.work.order')
    electrical_work_scope_id = fields.Many2one('product.product',
                                               string='Electrical Scope',
                                               domain=[('is_electrical', '=',
                                                        True)])
    electrical_work_scope_code = fields.Char(string='Item code')
    electrical_work_scope_description = fields.Char(string='Item description')
    electrical_work_scope_price = fields.Float(string='Amount')
    electrical_work_qty = fields.Float(string='Quantity')
    electrical_work_tax = fields.Many2many('account.tax', string='VAT')
    electrical_work_tax_amount = fields.Float(string='VAT Amount')
    electrical_work_subtotal = fields.Float(string='Subtotal')
    electrical_work_total = fields.Float(string='Total')
    warranty_status = fields.Selection(
        [('no', 'No'),
         ('yes', 'Yes'),
         ], string='Warranty', default='no')


class StockMove(models.Model):
    _inherit = 'stock.move'

    electrical_order_move_id = fields.Many2one('electrical.work.order',
                                               string="Order Reference")


class ElectricalTechnicianDetails(models.Model):
    _name = 'electrical.technician.line'
    _description = 'Technician Details'

    work_order_id = fields.Many2one('electrical.work.order')
    technician_id = fields.Many2one('hr.employee', string='Technician')
    technician_phone = fields.Char(related='technician_id.work_phone', string='Phone')
