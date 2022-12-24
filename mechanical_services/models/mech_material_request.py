# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MaterialRequest(models.Model):
    _name = 'mechanical.material.request'
    _rec_name = 'name'
    _description = 'Material Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string="Customer")
    date = fields.Date(string="Date")
    site_reference = fields.Many2many('mechanical.site.ref', string="Site Reference")
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    project_id = fields.Many2one('project.project', string="Project", default=lambda self: self.env.ref(
        'project_data.project_project_mechanical').id)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    pending_list = fields.Many2one('mechanical.work.order', string="Pending List",
                                   help="Pending Order Lists to create Request", copy=False)
    material_bom_line = fields.One2many('mechanical.material.request.line', 'material_request_id',
                                        string="Bill Of Quantities")
    state = fields.Selection([
        ('not send', 'Not Send'),
        ('send', 'Send')], string='State',
        copy=False, default='not send')
    purchase_order_count = fields.Integer(compute='_compute_purchase_order_count')

    def _compute_purchase_order_count(self):
        for material in self:
            material.purchase_order_count = material.env['purchase.order'].search_count(
                [('origin', '=', material.name)]) or 0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('mechanical.material.request' or _('New'))
        result = super(MaterialRequest, self).create(vals)
        return result

    def action_send_email(self):
        """Send material request details to the customer"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('mechanical_services.email_template_mechanical_material_request')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        # ctx = {
        #     'default_model': 'mechanical.material.request',
        #     'default_template_id': self.env.ref('mechanical_services.email_template_mechanical_material_request').id,
        # }
        ctx = {
            'default_model': 'mechanical.material.request',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        self.state = 'send'
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

    # def action_send_email(self):
    #     """Send material request details to the customer"""
    #     self.ensure_one()
    #     print("send..................................")
    #     ir_model_data = self.env['ir.model.data']
    #
    #     try:
    #         compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
    #     except ValueError:
    #         compose_form_id = False
    #     ctx = {
    #         'default_model': 'mechanical.material.request',
    #         'default_template_id': self.env.ref('mechanical_services.email_template_mechanical_material_request').id,
    #     }
    #     self.state = 'send'
    #     return {
    #         'name': _('Compose Email'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form_id, 'form')],
    #         'view_id': compose_form_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    def generate_purchase_order(self):
        order_line_ids = []
        for line in self.material_bom_line:
            vals = {
                'product_id': line.work_spare_parts_id.id,
                'product_uom_qty': line.work_spare_parts_qty,
                'product_price_unit': line.work_spare_parts_unit_price,
                'product_uom': line.work_spare_unit.id,
                'price_subtotal': line.work_spare_parts_qty * line.work_spare_parts_unit_price,
            }
            order_line_ids.append(vals)
        ctx = {
            'default_order_line_ids': order_line_ids,
            'default_origin': self.name,
        }
        view_id = self.env.ref('mechanical_services.view_mech_po_wizard').id
        return {
            'name': _('Create Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mech.po.wizard',
            'views': [[view_id, 'form']],
            'target': 'new',
            'context': ctx,
        }

    def button_view_purchase(self):
        """Function for viewing the purchase records of the corresponding
        material requests"""
        self.ensure_one()
        return {
            'name': 'Purchase orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('origin', '=', self.name)],
            'context': {'create': False},
            'target': 'current'
        }


class WorkOrderBomLine(models.Model):
    """Order Line for Material Request"""
    _name = 'mechanical.material.request.line'
    _description = 'Material Request Line'

    material_request_id = fields.Many2one('mechanical.material.request', string="Material Request")
    work_spare_parts_id = fields.Many2one('product.product', string="Product")
    work_spare_parts_unit_price = fields.Float(string="Price")
    work_spare_unit = fields.Many2one('uom.uom', string="Unit", related='work_spare_parts_id.uom_id')
    work_spare_parts_qty = fields.Float(string="Quantity")
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='work_spare_parts_id.currency_id')
