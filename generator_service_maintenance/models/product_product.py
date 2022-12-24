# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    is_generator = fields.Boolean(string='Is Generator')
    engine_fsd_number = fields.Char(string='Generator Name')
    generator_image = fields.Binary()
    generator_serial_number = fields.Char(string='Generator Serial No')
    generator_kva_ph = fields.Char(string='Generator KVA/PH')
    engine_serial_number = fields.Char(string='Engine Serial No')
    engine_model = fields.Char(string='Engine Model')
    alternator_serial_number = fields.Char(string='Alternator Serial Number')
    alternator_frame_size = fields.Char(string='Alternator Frame Size')
    panel_amf = fields.Char(string='Panel - AMF/Manual (PIU)')
    panel_amf_make = fields.Char(string='AMF Panel / PIU Make')
    last_hours = fields.Char(string='Last Serv.Hours & Date')
    service_hour_history_ids = fields.One2many('service.history.line', 'service_history_id')
    generator_spare_parts_ids = fields.One2many('generator.spare.line', 'spare_parts_id')
    routine_maintenance_cost = fields.Float(string='Yearly Routine Maintenance')
    routine_month_cost = fields.Float(string='Monthly Routine Maintenance', compute='_compute_monthly_charge')
    monitor_service_cost = fields.Float(string='Yearly Monitor Service')
    monitor_month_cost = fields.Float(string='Monthly Monitor Service')
    deployment_service_cost = fields.Float(string='Yearly Deployment Service')
    deployment_month_cost = fields.Float(string='Monthly Deployment Service')
    breakdown_service_cost = fields.Float(string='Yearly Breakdown Service')
    breakdown_month_cost = fields.Float(string='Monthly Breakdown Service')
    quotation_count = fields.Integer(compute='_compute_quotation_count', string="Quotation Count", type='integer')
    service_count = fields.Integer(compute='_compute_service_count', string="Service Count", type='integer')

    @api.depends('routine_maintenance_cost', 'deployment_service_cost', 'breakdown_service_cost',
                 'monitor_service_cost')
    def _compute_monthly_charge(self):
        """Function for calculating the monthly charge"""
        for generator in self:
            generator.routine_month_cost = generator.routine_maintenance_cost / 12
            generator.monitor_month_cost = generator.monitor_service_cost / 12
            generator.deployment_month_cost = generator.deployment_service_cost / 12
            generator.breakdown_month_cost = generator.breakdown_service_cost / 12

    def _compute_quotation_count(self):
        """In this compute function counts the number of quotations corresponding to the
        generator"""
        for record in self:
            record.quotation_count = record.env['service.quotation'].search_count(
                [('service_generator_id', '=', record.id)]) or 0

    def _compute_service_count(self):
        """In this compute function counts the number of services corresponding to the
        generator"""
        for record in self:
            record.service_count = record.env['generator.service'].search_count(
                [('service_generator_id', '=', record.id)]) or 0

    def button_quotation(self):
        """In this the button redirect to the view of the quotations which
        the current generator included"""
        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'service.quotation',
            'domain': [('service_generator_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    def button_service(self):
        """In this the button redirect to the view of the services which
        the current generator included"""
        return {
            'name': 'Service',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'generator.service',
            'domain': [('service_generator_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }


class ServiceHistoryLine(models.Model):
    _name = "service.history.line"
    _description = 'Service history line'

    service_history_id = fields.Many2one('product.product')
    service_hour = fields.Float(string="Hours")
    service_date = fields.Date(string="Date")
    service_type = fields.Selection([
        ('routine', 'Routine Maintenance'),
        ('monitor', 'Monitor Service'),
        ('deployment', 'Deployment Service'),
        ('breakdown', 'Breakdown Service'),
    ], string='Service Type')
    service_status = fields.Selection([('approved', 'Approved'), ('not_approved', 'Not Approved')],
                                      string='Status', copy=False)


class GeneratorSpareLine(models.Model):
    _name = "generator.spare.line"
    _description = 'Generator spare line'

    spare_parts_id = fields.Many2one('product.product')
    generator_spare_parts = fields.Many2one('product.product', string="Spares", domain="[('type', '=', 'product')]")
    generator_spare_parts_quantity = fields.Float(string='Quantity', default=1.0)
    generator_spare_parts_uom = fields.Many2one('uom.uom', string='Unit')
    generator_spare_parts_cost = fields.Float(string="Unit Price")
    service_days = fields.Integer(string="Service Period")

    @api.onchange('generator_spare_parts')
    def onchange_generator_spare_parts(self):
        """In this onchange function loads the unit and cost defined in the product
        form to the spare parts details"""
        self.generator_spare_parts_uom = self.generator_spare_parts.uom_id
        self.generator_spare_parts_cost = self.generator_spare_parts.lst_price
