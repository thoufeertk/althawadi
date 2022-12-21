# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class WorkshopMaterialRequest(models.Model):
    _name = 'workshop.material.request'
    _rec_name = 'name'
    _description = 'Material Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string="Customer")
    date = fields.Date(string="Service Date")
    order_priority = fields.Selection([('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
                                      default='high', string="Service Priority")
    pending_list_id = fields.Many2one('workshop.order', string="Work Order",
                                      help="Corresponding Order", copy=False)
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    project_id = fields.Many2one('project.project', string="Project", default=lambda self:
                                    self.env.ref('project_data.project_project_workshop').id)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    material_bom_line = fields.One2many('work.material.request.bom.line', 'material_request_id', string="Spare Parts")
    state = fields.Selection([
        ('not send', 'Not Send'),
        ('send', 'Send')], string='State',
        copy=False, default='not send')
    report_check = fields.Boolean(string="Check")
    purchase_order_count = fields.Integer(compute='_compute_purchase_order_count')

    def _compute_purchase_order_count(self):
        for material in self:
            material.purchase_order_count = material.env['purchase.order'].search_count(
                [('origin', '=', material.name)]) or 0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('workshop.material.request' or _('New'))
        result = super(WorkshopMaterialRequest, self).create(vals)
        return result

    def action_send_email(self):
        """Send material request details to the customer"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'workshop.material.request',
            'default_template_id': self.env.ref('workshop.'
                                                'email_template_workshop_material_request').id,
            'mark_request_as_sent': True
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

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_request_as_sent'):
            self.filtered(lambda o: o.state == 'not send').write({'state': 'send'})
        return super(WorkshopMaterialRequest, self).message_post(**kwargs)

    def print_request(self):
        """Printing the material request"""
        self.write({'report_check': True})
        return self.env.ref('workshop.action_report_material_request').report_action(self)

    def update_report_value(self):
        if self.report_check:
            self.write({'report_check': False})
        return False

    def generate_purchase_order(self):
        order_line_ids = []
        for line in self.material_bom_line:
            vals = {
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_price_unit': line.price,
                'product_uom': line.product_unit_measure.id,
                'price_subtotal': line.quantity * line.price,
            }
            order_line_ids.append(vals)
        ctx = {
            'default_order_line_ids': order_line_ids,
            'default_origin': self.name,
        }
        view_id = self.env.ref('workshop.view_workshop_purchase_order_wizard').id
        return {
            'name': _('Create Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'create.workshop.purchase',
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


class WorkshopBomLine(models.Model):
    """Order Line for Material Request"""
    _name = 'work.material.request.bom.line'
    _description = 'Material Request Line'

    material_request_id = fields.Many2one('workshop.material.request', string="Material Request")
    product_id = fields.Many2one('product.product', string="Product", ondelete="restrict")
    price = fields.Monetary(string="Price", currency_field='currency_id')
    quantity = fields.Float(string="Quantity")
    product_unit_measure = fields.Many2one('uom.uom', string="Unit", related='product_id.uom_id')
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='product_id.currency_id')
