import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_generator_sale = fields.Boolean(string='Generator Sales')
    gen_service_type = fields.Selection([('monitor', 'Monitor Service'),
                                         ('deployment', 'Deployment Service'),
                                         ('breakdown', 'Breakdown Service'),
                                         ('routine', 'Routine Maintenance'),
                                         ], string='Service Type')
    allocated_no_service = fields.Integer(string='Allocated Service')
    remaining_no_service = fields.Integer(string='Remaining Service', readonly=1)
    availability_reason = fields.Char(string='Availability Status', compute='_compute_availability', readonly=False)
    service_bld_number = fields.Char(string='Bld No./Sub Station No')
    service_road_number = fields.Char(string='Road Number')
    service_area_number = fields.Char(string='Area Number')
    service_period_type = fields.Selection([('monthly', 'Monthly'),
                                            ('yearly', 'Yearly'),
                                            ], string='Period Type')

    @api.depends('remaining_no_service')
    def _compute_availability(self):
        for sale in self:
            if sale.remaining_no_service == 0:
                sale.availability_reason = 'Available'
            else:
                sale.availability_reason = 'Not Available'

    @api.onchange('gen_service_type', 'service_period_type')
    def _onchange_gen_service_type(self):
        line = self.order_line
        if self.gen_service_type:
            if len(line) < 1 or not self.partner_id:
                raise UserError(_("Select a Generator and Customer !"))
            generator = self.order_line.mapped('product_id')
            if generator:
                has_warranty = False
                generator = generator[0]
                old_service = self.env['generator.service'].search([('service_customer', '=', self.partner_id.id)],
                                                                   order='id desc', limit=1)
                if old_service and old_service.warranty_days != 0:
                    warranty_days = old_service.warranty_days
                    old_date = old_service.service_date.date()
                    next_service_date = old_date + datetime.timedelta(days=warranty_days)
                    today = datetime.datetime.now().date()
                    if next_service_date >= today:
                        for line in self.order_line:
                            line.price_unit = 0
                            line._compute_amount()
                            line._get_price_reduce()
                            line._onchange_discount()
                            has_warranty = True
                if not has_warranty:
                    if self.gen_service_type == 'monitor':
                        if self.service_period_type == 'yearly':
                            line.price_unit = generator.monitor_service_cost
                        if self.service_period_type == 'monthly':
                            line.price_unit = generator.monitor_month_cost
                    if self.gen_service_type == 'deployment':
                        if self.service_period_type == 'yearly':
                            line.price_unit = generator.deployment_service_cost
                        if self.service_period_type == 'monthly':
                            line.price_unit = generator.deployment_month_cost
                    if self.gen_service_type == 'breakdown':
                        if self.service_period_type == 'yearly':
                            line.price_unit = generator.breakdown_service_cost
                        if self.service_period_type == 'monthly':
                            line.price_unit = generator.breakdown_month_cost
                    if self.gen_service_type == 'routine':
                        if self.service_period_type == 'yearly':
                            line.price_unit = generator.routine_maintenance_cost
                        if self.service_period_type == 'monthly':
                            line.price_unit = generator.routine_month_cost
                    line._compute_amount()
                    line._get_price_reduce()
                    line._onchange_discount()

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.is_generator_sale:
            for line in self.order_line:
                self.partner_id.is_generator_customer = True
                if not self.partner_id.generator_id:
                    self.partner_id.update({'generator_id': [(6, 0, line.product_id.ids)]})
                # self.partner_id._onchange_generator_id()
            self.remaining_no_service = self.allocated_no_service
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        domain = super(SaleOrderLine, self).product_id_change()
        if self.order_id.is_generator_sale:
            return {'domain': {'product_id': [('is_generator', '=', True), ('type', '=', 'service')]}}
        return domain
