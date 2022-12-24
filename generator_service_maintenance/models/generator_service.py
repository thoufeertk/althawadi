# -*- coding: utf-8 -*-
import datetime
from datetime import date

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class GeneratorService(models.Model):
    _name = "generator.service"
    _rec_name = 'name'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Generator Service'

    def _get_customer_generators(self):
        if self.service_customer:
            return [('id', 'in', self.service_customer.generator_id.ids)]
        else:
            return []

    service_generator_id = fields.Many2one('product.product',
                                           string='Generator', domain="[('id', '=', 0)]")
    service_engine_fsd_number = fields.Char(string='Generator Name', related='service_generator_id.engine_fsd_number',
                                            readonly=False)
    service_generator_serial_number = fields.Char(string='Generator Serial No', related='service_generator_id'
                                                                                        '.generator_serial_number',
                                                  readonly=False)
    service_generator_kva_ph = fields.Char(string='Generator KVA/PH', related='service_generator_id.generator_kva_ph',
                                           readonly=False)
    service_engine_serial_number = fields.Char(string='Engine Serial No',
                                               related='service_generator_id.engine_serial_number',
                                               readonly=False)
    service_engine_model = fields.Char(string='Engine Model', related='service_generator_id.engine_model',
                                       readonly=False)
    service_alternator_serial_number = fields.Char(string='Alternator Serial Number', related='service_generator_id'
                                                                                              '.alternator_serial_number',
                                                   readonly=False)
    service_alternator_frame_size = fields.Char(string='Alternator Frame Size',
                                                related='service_generator_id.alternator_frame_size', readonly=False)
    service_panel_amf = fields.Char(string='Panel - AMF/Manual (PIU)',
                                    related='service_generator_id.panel_amf', readonly=False)
    service_panel_amf_make = fields.Char(string='AMF Panel / PIU Make',
                                         related='service_generator_id.panel_amf_make', readonly=False)
    service_last_hours = fields.Char(string='Last Serv.Hours & Date',
                                     related='service_generator_id.last_hours', readonly=False)
    service_date = fields.Datetime(string='Service Date', default=fields.Datetime.now, required=True)
    service_customer = fields.Many2one('res.partner', string='Customer',
                                       domain="[('is_generator_customer', '=', True)]", required=True)
    service_type = fields.Selection([('monitor', 'Monitor Service'),
                                     ('deployment', 'Deployment Service'),
                                     ('breakdown', 'Breakdown Service'),
                                     ('routine', 'Routine Maintenance'),
                                     ], string='Service Type', required=True)

    service_estimated_cost = fields.Float(string='Service Cost')
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    service_generator_name = fields.Char(string='Generator Name', invisible=1)
    service_generator_image = fields.Binary()
    service_bld_number = fields.Char(string='Bld No./Sub Station No')
    service_road_number = fields.Char(string='Road Number')
    service_area_number = fields.Char(string='Area Number')
    service_area = fields.Char(string='Area')
    service_generator_running_hours = fields.Float(string='Running Hours')
    service_generator_piu_running_hours = fields.Float(string='PIU Running Hrs')
    service_breakdown_date = fields.Date(string='Breakdown Date')
    service_initial_fault = fields.Char(string='Initial Fault Found')
    service_rectifications = fields.Char(string='Rectifications')
    service_generator_spare_parts_ids = fields.One2many('stock.move', 'generator_spare_move_id', string="Spare Parts")
    technician_details_ids = fields.One2many('technician.details.line', 'service_technician_id')
    gen_service_visual_rust = fields.Boolean(string='R-Visual Inspection for Rust')
    check_gen_service_visual_rust = fields.Boolean(string='Checking R-Visual Inspection for Rust',
                                                   related='service_customer.gen_service_visual_rust')
    dec_gen_service_visual_rust = fields.Many2one('check.point.details')
    gen_service_check_any_deposition = fields.Boolean(string='Check Any Deposition (Oil, diesel, dust)')
    check_gen_service_check_any_deposition = fields.Boolean(string='Checking Any Deposition (Oil, diesel, dust)',
                                                            related='service_customer.gen_service_check_any_deposition')
    dec_gen_service_check_any_deposition = fields.Many2one('check.point.details')
    gen_service_check_any_cleanliness = fields.Boolean(string='Check the Cleanliness of the generator set')
    check_gen_service_check_any_cleanliness = fields.Boolean(string='Checking the Cleanliness of the generator set',
                                                             related='service_customer'
                                                                     '.gen_service_check_any_cleanliness')
    dec_gen_service_check_any_cleanliness = fields.Many2one('check.point.details')
    lub_service_lube_oil_level = fields.Boolean(string='Check for oil level')
    check_lub_service_lube_oil_level = fields.Boolean(string='Checking for oil level',
                                                      related='service_customer.lub_service_lube_oil_level')
    dec_lub_service_lube_oil_level = fields.Many2one('check.point.details')
    lub_service_lube_engine_oil_level = fields.Boolean(string='Check engine oil level')
    check_lub_service_lube_engine_oil_level = fields.Boolean(string='Checking engine oil level',
                                                             related='service_customer'
                                                                     '.lub_service_lube_engine_oil_level')
    dec_lub_service_lube_engine_oil_level = fields.Many2one('check.point.details')
    lub_service_lube_engine_oil_condition = fields.Boolean(string='Check engine oil condition')
    check_lub_service_lube_engine_oil_condition = fields.Boolean(string='Checking engine oil condition',
                                                                 related='service_customer'
                                                                         '.lub_service_lube_engine_oil_condition')
    dec_lub_service_lube_engine_oil_condition = fields.Many2one('check.point.details')
    lub_service_lube_oil_filter = fields.Boolean(string='Check Oil filter')
    lub_service_lube_governer_oil = fields.Boolean(string='Check Governer Oil')
    check_lub_service_lube_oil_filter = fields.Boolean(string='Checking Oil filter',
                                                       related='service_customer.lub_service_lube_oil_filter')
    check_lub_service_lube_governer_oil = fields.Boolean(string='Checking Governer Oil',
                                                         related='service_customer.lub_service_lube_governer_oil')
    dec_lub_service_lube_oil_filter = fields.Many2one('check.point.details')
    dec_lub_service_lube_governer_oil = fields.Many2one('check.point.details')
    lub_service_lube_oil_pressure = fields.Boolean(string='Check & record oil pressure')
    check_lub_service_lube_oil_pressure = fields.Boolean(string='Checking & record oil pressure',
                                                         related='service_customer.lub_service_lube_oil_pressure')
    dec_lub_service_lube_oil_pressure = fields.Many2one('check.point.details')
    lub_service_hydraulic_governor_pressure = fields.Boolean(string='R-Check hydraulic governor oil level')
    check_lub_service_hydraulic_governor_pressure = fields.Boolean(
        string='Checking R-Check hydraulic governor oil level',
        related='service_customer'
                '.lub_service_hydraulic_governor_pressure')
    dec_lub_service_hydraulic_governor_pressure = fields.Many2one('check.point.details')
    fuel_service_leaks = fields.Boolean(string='Check for fuel leaks')
    check_fuel_service_leaks = fields.Boolean(string='Checking for fuel leaks',
                                              related='service_customer.fuel_service_leaks')
    dec_fuel_service_leaks = fields.Many2one('check.point.details')
    fuel_service_main_tank_level = fields.Boolean(string='Check main tank level (S.S)')
    check_fuel_service_main_tank_level = fields.Boolean(string='Checking main tank level (S.S)',
                                                        related='service_customer.fuel_service_main_tank_level')
    dec_fuel_service_main_tank_level = fields.Many2one('check.point.details')
    fuel_service_day_tank_level = fields.Boolean(string='Check day tank level (S.S)')
    check_fuel_service_day_tank_level = fields.Boolean(string='Checking day tank level (S.S)',
                                                       related='service_customer.fuel_service_day_tank_level')
    dec_fuel_service_day_tank_level = fields.Many2one('check.point.details')
    fuel_service_transfer_pump = fields.Boolean(string='Check fuel transfer pump')
    check_fuel_service_transfer_pump = fields.Boolean(string='Checking fuel transfer pump',
                                                      related='service_customer.fuel_service_transfer_pump')
    dec_fuel_service_transfer_pump = fields.Many2one('check.point.details')
    fuel_service_drain_sediment = fields.Boolean(string='Drain sediments from tank (S.S)')
    check_fuel_service_drain_sediment = fields.Boolean(string='Checking Drain sediments from tank (S.S)',
                                                       related='service_customer.fuel_service_drain_sediment')
    dec_fuel_service_drain_sediment = fields.Many2one('check.point.details')
    fuel_service_governor_linkage = fields.Boolean(string='Check governor & linkage to pump')
    check_fuel_service_governor_linkage = fields.Boolean(string='Checking governor & linkage to pump',
                                                         related='service_customer.fuel_service_governor_linkage')
    dec_fuel_service_governor_linkage = fields.Many2one('check.point.details')
    fuel_service_lines_connection = fields.Boolean(string='Check fuel lines & connection')
    check_fuel_service_lines_connection = fields.Boolean(string='Checking fuel lines & connection',
                                                         related='service_customer.fuel_service_lines_connection')
    dec_fuel_service_lines_connection = fields.Many2one('check.point.details')
    fuel_service_filter = fields.Boolean(string='Check fuel filter')
    check_fuel_service_filter = fields.Boolean(string='Checking fuel filter',
                                               related='service_customer.fuel_service_filter')
    dec_fuel_service_filter = fields.Many2one('check.point.details')
    engine_service_unusual_vibration = fields.Boolean(string='Check engine unusual vibration')
    check_engine_service_unusual_vibration = fields.Boolean(string='Checking engine unusual vibration',
                                                            related='service_customer.engine_service_unusual_vibration')
    dec_engine_service_unusual_vibration = fields.Many2one('check.point.details')
    engine_service_mounting_hardware = fields.Boolean(string='Check engine tightening mounting hardware')
    check_engine_service_mounting_hardware = fields.Boolean(string='Checking engine tightening mounting hardware',
                                                            related='service_customer.engine_service_mounting_hardware')
    dec_engine_service_mounting_hardware = fields.Many2one('check.point.details')
    cooling_service_coolant_leaks = fields.Boolean(string='Check coolant leaks')
    check_cooling_service_coolant_leaks = fields.Boolean(string='Checking coolant leaks',
                                                         related='service_customer.cooling_service_coolant_leaks')
    dec_cooling_service_coolant_leaks = fields.Many2one('check.point.details')
    cooling_service_radiator_air_passageway = fields.Boolean(string='Check radiator air passageway for any restriction')
    check_cooling_service_radiator_air_passageway = fields.Boolean(
        string='Checking radiator air passageway for any restriction',
        related='service_customer.cooling_service_radiator_air_passageway')
    dec_cooling_service_radiator_air_passageway = fields.Many2one('check.point.details')
    cooling_service_hoses_connections = fields.Boolean(string='Check hoses & connections')
    check_cooling_service_hoses_connections = fields.Boolean(string='Checking hoses & connections',
                                                             related='service_customer.cooling_service_coolant_level')
    dec_cooling_service_hoses_connections = fields.Many2one('check.point.details')
    cooling_service_coolant_level = fields.Boolean(string='Check Coolant level')
    check_cooling_service_coolant_level = fields.Boolean(string='Checking Coolant level',
                                                         related='service_customer.cooling_service_coolant_level')
    dec_cooling_service_coolant_level = fields.Many2one('check.point.details')
    dec_pressure_check = fields.Char(string="Pressure")
    dec_temperature_check = fields.Char(string="Temperature")
    cooling_service_belt_condition_tension = fields.Boolean(string='Check belt condition & tension')
    check_cooling_service_belt_condition_tension = fields.Boolean(string='Checking belt condition & tension',
                                                                  related='service_customer.cooling_service_belt_condition_tension')
    dec_cooling_service_belt_condition_tension = fields.Many2one('check.point.details')
    cooling_service_grease_leak = fields.Boolean(string='Check wobble & grease leak in fan Hub & drive pulley (S.S)')
    check_cooling_service_grease_leak = fields.Boolean(
        string='Checking wobble & grease leak in fan Hub & drive pulley (S.S)',
        related='service_customer.cooling_service_grease_leak')
    dec_cooling_service_grease_leak = fields.Many2one('check.point.details')
    cooling_service_operation_heater = fields.Boolean(string='Check operation of Coolant heater')
    check_cooling_service_operation_heater = fields.Boolean(string='Checking operation of Coolant heater',
                                                            related='service_customer.cooling_service_operation_heater')
    dec_cooling_service_operation_heater = fields.Many2one('check.point.details')
    air_service_leaks = fields.Boolean(string='Check for Air Leaks')
    check_air_service_leaks = fields.Boolean(string='Checking for Air Leaks',
                                             related='service_customer.air_service_leaks')
    dec_air_service_leaks = fields.Many2one('check.point.details')
    air_service_cleaner_passage = fields.Boolean(string='Check Air cleaner passageway for any restriction')
    check_air_service_cleaner_passage = fields.Boolean(string='Checking Air cleaner passageway for any restriction',
                                                       related='service_customer.air_service_cleaner_passage')
    dec_air_service_cleaner_passage = fields.Many2one('check.point.details')
    air_service_piping_connection = fields.Boolean(string='Check piping & connections')
    check_air_service_piping_connection = fields.Boolean(string='Checking piping & connections',
                                                         related='service_customer.air_service_piping_connection')
    dec_air_service_piping_connection = fields.Many2one('check.point.details')
    electrical_service_battery = fields.Boolean(string='Check Check Battery')
    check_electrical_service_battery = fields.Boolean(string='Checking Check Battery',
                                                      related='service_customer.electrical_service_electrolyte')
    dec_electrical_service_battery = fields.Many2one('check.point.details')
    electrical_service_electrolyte = fields.Boolean(string='Check electrolyte level')
    check_electrical_service_electrolyte = fields.Boolean(string='Checking electrolyte level',
                                                          related='service_customer.electrical_service_electrolyte')
    dec_electrical_service_electrolyte = fields.Many2one('check.point.details')
    electrical_service_gravity = fields.Boolean(string='Check specific gravity')
    check_electrical_service_gravity = fields.Boolean(string='Checking specific gravity',
                                                      related='service_customer.electrical_service_electrolyte')
    dec_electrical_service_gravity = fields.Many2one('check.point.details')
    electrical_service_charging_system = fields.Boolean(string='R-Check Charging system')
    check_electrical_service_charging_system = fields.Boolean(string='R-Checking Charging system',
                                                              related='service_customer.electrical_service_charging_system')
    dec_electrical_service_charging_system = fields.Many2one('check.point.details')
    electrical_service_load_breaker = fields.Boolean(string='R-Check Load breaker')
    check_electrical_service_load_breaker = fields.Boolean(string='R-Checking Load breaker',
                                                           related='service_customer.electrical_service_load_breaker')
    dec_electrical_service_load_breaker = fields.Many2one('check.point.details')
    generator_service_passage = fields.Boolean(string='Check air inlet & outlet passageway (Canopy/S.S louvers)')
    check_generator_service_passage = fields.Boolean(
        string='Checking air inlet & outlet passageway (Canopy/S.S louvers)',
        related='service_customer.generator_service_passage')
    dec_generator_service_passage = fields.Many2one('check.point.details')
    generator_service_control_panel = fields.Boolean(string='Check control panel lamps')
    check_generator_service_control_panel = fields.Boolean(string='Checking control panel lamps',
                                                           related='service_customer.generator_service_control_panel')
    dec_generator_service_control_panel = fields.Many2one('check.point.details')
    starting_service_auto_manual = fields.Boolean(
        string="Start up the generator with selector switch set in auto/manual")
    check_starting_service_auto_manual = fields.Boolean(
        string="Checking Start up the generator with selector switch set in auto/manual",
        related='service_customer.starting_service_auto_manual')
    dec_starting_service_auto_manual = fields.Many2one('check.point.details')
    starting_service_under_voltage = fields.Boolean(string="Check for under voltage")
    check_starting_service_under_voltage = fields.Boolean(string="Checking for under voltage",
                                                          related='service_customer.starting_service_under_voltage')
    dec_starting_service_under_voltage = fields.Many2one('check.point.details')
    starting_service_terminal_voltage = fields.Boolean(string="Check and record terminal voltage")
    check_starting_service_terminal_voltage = fields.Boolean(string="Checking and record terminal voltage",
                                                             related='service_customer'
                                                                     '.starting_service_terminal_voltage')
    dec_starting_service_terminal_voltage = fields.Many2one('check.point.details')
    starting_service_frequency = fields.Boolean(string="Check and record Frequency")
    check_starting_service_frequency = fields.Boolean(string="Checking and record Frequency",
                                                      related='service_customer.starting_service_frequency')
    dec_starting_service_frequency = fields.Many2one('check.point.details')
    starting_service_load_current = fields.Boolean(string="Check load current (S.S)")
    check_starting_service_load_current = fields.Boolean(string="Checking load current (S.S)",
                                                         related='service_customer.starting_service_load_current')
    dec_starting_service_load_current = fields.Many2one('check.point.details')
    starting_service_operation_total_hours = fields.Boolean(string="Service operation total hours")
    check_starting_service_operation_total_hours = fields.Boolean(string="Checking Service operation total hours",
                                                                  related='service_customer'
                                                                          '.starting_service_operation_total_hours')
    dec_starting_service_operation_total_hours = fields.Many2one('check.point.details')
    alarm_service_test_reset = fields.Boolean(string='Test and reset all alarms')
    check_alarm_service_test_reset = fields.Boolean(string='Testing and reset all alarms',
                                                    related='service_customer.alarm_service_test_reset')
    dec_alarm_service_test_reset = fields.Many2one('check.point.details')
    alternator_service_insulation = fields.Boolean(string='Check & record alternator insulation resistance (IR)')
    check_alternator_service_insulation = fields.Boolean(
        string='Checking & record alternator insulation resistance (IR)',
        related='service_customer.alternator_service_insulation')
    dec_alternator_service_insulation = fields.Many2one('check.point.details')
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    state = fields.Selection(
        [('waiting', 'Waiting For Approve'), ('draft', 'Draft'), ('waiting_material', 'Waiting For Material'),
         ('running', 'Running'),
         ('submit', 'Submit'),
         ('approve', 'Serviced'),
         ('invoice', 'Invoiced'), ('reject', 'Rejected')],
        string="Status", readonly=True, default='draft', copy=False, track_visibility='onchange')

    amc_check = fields.Boolean(default=False)
    generator_spare_parts_ids = fields.One2many('generator.spare.line', 'spare_parts_id')
    check_quotation_visibility = fields.Boolean(default=False)
    quotation_count = fields.Integer(compute='_compute_count', string="Quotation Count", type='integer')
    invoice_count = fields.Integer(compute='_compute_count', string='Invoice Count', type='integer')
    material_request_count = fields.Integer(compute='_compute_count', string='Material Request count',
                                            default=0)
    warranty_days = fields.Integer(string='Warranty in Days')
    gen_sale_order_id = fields.Many2one('sale.order', string="Job Order")
    generator_service_picking_id = fields.Many2one('stock.picking', string='Related Picking')

    # address
    street = fields.Char(string='street')
    street2 = fields.Char(string='street2')
    zip = fields.Char(change_default=True)
    city = fields.Char(string='city')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char(string='email')
    phone = fields.Char(string='phone')
    mobile = fields.Char(string='mobile')
    # amc contract reference
    amc_contract_id = fields.Many2one('annual.maintenance.contract', string="Running AMC Contract")

    @api.onchange('gen_sale_order_id')
    def _onchange_gen_sale_order_id(self):
        for rec in self:
            if rec.gen_sale_order_id:
                rec.service_bld_number = rec.gen_sale_order_id.service_bld_number
                rec.service_road_number = rec.gen_sale_order_id.service_road_number
                rec.service_area_number = rec.gen_sale_order_id.service_area_number
                rec.service_customer = rec.gen_sale_order_id.partner_id.id
                rec.service_generator_id = rec.gen_sale_order_id.order_line[0].product_id.id if rec.gen_sale_order_id.order_line else False

    @api.model
    def create(self, vals):
        """Here create function is override for generating sequence for the generator.service"""
        vals['name'] = self.env['ir.sequence'].next_by_code('generator.service')
        return super(GeneratorService, self).create(vals)

    @api.onchange('service_customer')
    def _onchange_service_customer(self):
        """This function checks whether a customer have amc contract or not.if there is no amc contract for customer
        then one can generate quotation"""
        self.amc_check = False
        self.service_type = False
        customer = self.service_customer
        data = ['street', 'street2', 'city', 'state_id', 'zip', 'country_id']
        if customer:
            values = customer.read(data)[0]
            values.pop('id')
            self.update(values)
        self.service_generator_spare_parts_ids = [(5, 0, 0)]
        annual_maintenance_id = self.env['annual.maintenance.contract'].search(
            [('contract_partner_id', '=', self.service_customer.id)])
        for amc_line in annual_maintenance_id:
            if amc_line.state == 'running':
                self.amc_check = False
                self.amc_contract_id = amc_line.id
                self.state = 'draft'
            else:
                self.amc_check = True
                self.state = 'waiting'
        if not annual_maintenance_id:
            self.amc_check = True
            self.state = 'waiting'
        if self.service_customer:
            domain = {'domain': {'service_generator_id': [('id', 'in', self.service_customer.generator_id.ids)]}}
            return domain

    def button_generator_task(self):
        return {
            'name': 'Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('generator_service', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }

    def _compute_count(self):
        for service_id in self:
            service_id.quotation_count = service_id.env['service.quotation'].search_count(
                [('reference', '=', service_id.id)]) or 0
            service_id.invoice_count = 0
            service_id.material_request_count = self.env['generator.material.request'].search_count(
                [('pending_list_id', '=', service_id.id)])

    def button_quotation(self):
        """This is the function of the smart button which redirect to the quotations related to the current service"""
        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'service.quotation',
            'domain': [('reference', '=', self.name)],
            'context': {'create': False},
            'target': 'current'
        }

    def button_invoice(self):
        """This is the function of the smart button which redirect to the invoice related to the current service"""
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('invoice_origin', '=', self.name)],
            'context': {'create': False},
            'target': 'current'
        }

    def send_email(self):
        """
        This function opens a window to compose an email, with the editable sale template message loaded by default
        """
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('generator_service_maintenance.service_request_mail')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'generator.service',
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

    def print_service_report(self):
        """This function is for printing the current service form"""
        return self.env.ref('generator_service_maintenance.generator_document').report_action(self)

    def service_submit(self):
        """This is the function of the button submit which takes the input of the timesheet and create attendance
        for the corresponding technicians/helpers.Then it updates the service history of the generator used,finally
        change the state to submitted"""
        self.ensure_one()
        generator_details_ids = self.env['product.product'].browse(self.service_generator_id.id)
        service_date = self.service_date.date()
        generator_details_id = generator_details_ids.service_hour_history_ids.filtered(
            lambda l: l.service_type == self.service_type and l.service_date == service_date)
        total_hours = 0
        task = self.env['project.task'].search([('generator_service', '=', self.id)])
        if task:
            total_hours = task.effective_hours
        # if generator_details_id:
        #     generator_details_id.update({
        #         'service_type': self.service_type,
        #         'service_hour': generator_details_id.service_hour + total_hours,
        #         'service_date': service_date,
        #     })
        # else:
        service_hour_history_ids = [(0, 0, {
            'service_type': self.service_type,
            'service_hour': total_hours,
            'service_date': service_date,
        })]
        generator_details_ids.update({'service_hour_history_ids': service_hour_history_ids,
                                      'last_hours': str(service_date) + "," + str(total_hours) + " hours"})
        self.sudo().write({
            'state': 'submit'
        })
        return

    def service_start(self):
        """In this function process the stock moves of the spare parts used in the service
        and creating the related task
        """
        if self.service_type in ['breakdown', 'routine']:
            moves = self.service_generator_spare_parts_ids.filtered(
                lambda x: x.state not in ('done', 'cancel'))._action_confirm()
            moves._action_assign()
            MaterialRequest = self.env['generator.material.request']
            MaterialRequestLine = self.env['gen.material.request.bom.line']
            if any(line.state in ['confirmed', 'partially_available'] for line in
                   self.service_generator_spare_parts_ids):
                if self.material_request_count == 0:
                    vals = {
                        'partner_id': self.service_customer.id,
                        'service_type': self.service_type,
                        'date': self.service_date,
                        'pending_list_id': self.id,
                    }
                    request_id = MaterialRequest.create(vals)
                    MaterialRequestLine.create({
                                                   'product_id': material_line.product_id.id,
                                                   'quantity': material_line.product_uom_qty - material_line.reserved_availability,
                                                   'material_request_id': request_id.id,
                                                   'price': material_line.service_generator_spare_parts_cost,
                                               } for material_line in
                                               self.service_generator_spare_parts_ids.filtered(
                                                   lambda line: line.state in ['confirmed', 'partially_available']))
                    self.state = 'waiting_material'
            else:
                self.generator_service_picking_id.origin = self.name
                for line in self.service_generator_spare_parts_ids:
                    line.quantity_done = line.reserved_availability
                    line.generator_spare_move_id = self.id
                if self.generator_service_picking_id:
                    self.generator_service_picking_id.button_validate()
                    self.generator_service_picking_id.message_post_with_view('mail.message_origin_link',
                                                                             values={
                                                                                 'self': self.generator_service_picking_id,
                                                                                 'origin': self},
                                                                             subtype_id=self.env.ref('mail.mt_note').id)
        else:
            if self.generator_service_picking_id:
                self.generator_service_picking_id.sudo().unlink()
        if self.state != 'waiting_material':
            technician_list = []
            for technician_line in self.technician_details_ids:
                technician_list.append(technician_line.technician_id.id)
            if not technician_list:
                raise ValidationError("Choose atleast one technician!!!")

            self.env['project.task'].create({
                'name': self.name,
                'kanban_state': 'normal',
                'project_id': self.env.ref('project_data.project_project_generator').id,
                'partner_id': self.service_customer.id,
                'technician_ids': technician_list,
                'generator_service': self.id,
                'date_assign': date.today(),
            })
            self.sudo().write({
                'state': 'running'
            })

    def check_parts_availability(self):
        """
        Check the availability of Parts in stock.
        """
        moves = self.service_generator_spare_parts_ids.filtered(
            lambda x: x.state not in ('done', 'cancel'))._action_confirm()
        moves._action_assign()
        if any(line.state in ['confirmed', 'partially_available'] for line in self.service_generator_spare_parts_ids):
            self.state = 'waiting_material'
        else:
            self.state = 'draft'

    def create_quotation(self):
        """This is a button function for creating quotation related to the
        service(it create a record in service.quotation)"""
        Quotation = self.env['service.quotation']
        quotation_id = Quotation.create({
            'reference': self.id or False,
            'service_date': self.service_date,
            'service_customer': self.service_customer.id,
            'service_type': self.service_type,
            'service_estimated_cost': self.service_estimated_cost,
            'service_generator_id': self.service_generator_id.id,
            'service_engine_fsd_number': self.service_engine_fsd_number,
            'service_generator_name': self.service_generator_name,
            'service_generator_image': self.service_generator_image,
            'service_generator_serial_number': self.service_generator_serial_number,
            'service_generator_kva_ph': self.service_generator_kva_ph,
            'service_engine_serial_number': self.service_engine_serial_number,
            'service_engine_model': self.service_engine_model,
            'service_alternator_serial_number': self.service_alternator_serial_number,
            'service_alternator_frame_size': self.service_alternator_frame_size,
            'service_panel_amf': self.service_panel_amf,
            'service_panel_amf_make': self.service_panel_amf_make,
            'service_last_hours': self.service_last_hours,
            'service_road_number': self.service_road_number,
            'service_bld_number': self.service_bld_number,
            'service_area': self.service_area,
            'service_area_number': self.service_area_number,
            'service_generator_running_hours': self.service_generator_running_hours,
            'service_generator_piu_running_hours': self.service_generator_piu_running_hours,
            'service_breakdown_date': self.service_breakdown_date,
            'service_initial_fault': self.service_initial_fault,
            'service_rectifications': self.service_rectifications,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'state_id': self.state_id.id,
            'zip': self.zip,
            'country_id': self.country_id.id
        })
        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'service.quotation',
            'view_mode': 'form',
            'target': 'current',
            'res_id': quotation_id.id
        }

    @api.onchange('service_type')
    def _onchange_service_type(self):
        """This is the onchange function of the service_type which checks whether
        the corresponding service related to any of the maintenance contracts
        (quotation button visibility is calculated in this function)"""
        self.check_quotation_visibility = False
        show_warning = False
        if self.service_generator_id:
            # Create Picking and update move values
            if self.service_type in ['breakdown', 'routine']:
                if self.service_generator_id.service_hour_history_ids:
                    history = self.service_generator_id.service_hour_history_ids.filtered(
                        lambda hist: hist.service_type in ['breakdown', 'routine'])
                    if history:
                        history = history.sorted('service_date', reverse=True)[0]
                        old_date = history.service_date
                        message = ""
                        for line in self.service_generator_id.generator_spare_parts_ids:
                            if line.service_days != 0:
                                next_service_date = old_date + datetime.timedelta(days=line.service_days)
                                today = datetime.datetime.now().date()
                                if next_service_date > today:
                                    show_warning = True
                                    message = message + "Product : %s  -  Next Service Date : %s\n" % (
                                        line.generator_spare_parts.name, next_service_date)
                picking_type_id = self.env.ref('stock.picking_type_internal')
                location_id = picking_type_id.default_location_src_id.id
                destination_id = picking_type_id.default_location_dest_id.id
                if self.service_generator_id.generator_spare_parts_ids:
                    if not self.generator_service_picking_id:
                        if location_id and destination_id:
                            picking_vals = {
                                'partner_id': self.service_customer.id,
                                'picking_type_id': picking_type_id.id,
                                'location_id': location_id,
                                'location_dest_id': destination_id,
                            }
                            picking_id = self.env['stock.picking'].sudo().create(picking_vals)
                            self.generator_service_picking_id = picking_id.id
                    else:
                        picking_id = self.generator_service_picking_id
                    spare_parts_list = []
                    if not self.service_generator_spare_parts_ids:
                        for spare_part_id in self.service_generator_id.generator_spare_parts_ids:
                            vals = (0, 0, {
                                'picking_type_id': picking_type_id.id,
                                'picking_id': picking_id.id,
                                'name': spare_part_id.generator_spare_parts.name,
                                'product_id': spare_part_id.generator_spare_parts.id,
                                'product_uom_qty': spare_part_id.generator_spare_parts_quantity,
                                'product_uom': spare_part_id.generator_spare_parts_uom.id,
                                'service_generator_spare_parts_cost': spare_part_id.generator_spare_parts_cost,
                                'location_id': picking_type_id.default_location_src_id.id,
                                'location_dest_id': spare_part_id.generator_spare_parts.generator_stock_location.id,
                            })
                            spare_parts_list.append(vals)
                        self.update({'service_generator_spare_parts_ids': spare_parts_list})
            else:
                self.service_generator_spare_parts_ids = [(5, 0, 0)]
            cost = 0.0
            if self.service_type == 'monitor':
                cost = self.service_generator_id.monitor_service_cost
            elif self.service_type == 'deployment':
                cost = self.service_generator_id.deployment_service_cost
            elif self.service_type == 'breakdown':
                cost = self.service_generator_id.breakdown_service_cost
            elif self.service_type == 'routine':
                cost = self.service_generator_id.routine_maintenance_cost
            self.service_estimated_cost = cost
        if self.service_customer:
            annual_maintenance_contract_ids = self.env['annual.maintenance.contract'].search(
                [('contract_partner_id.id', '=', self.service_customer.id)])
            if annual_maintenance_contract_ids:
                for amc in annual_maintenance_contract_ids:
                    if self.service_type == 'monitor' and not amc.enable_monitor_service:
                        self.check_quotation_visibility = True
                        self.state = 'waiting'
                    elif self.service_type == 'deployment' and not amc.enable_deployment_service:
                        self.check_quotation_visibility = True
                        self.state = 'waiting'
                    elif self.service_type == 'breakdown' and not amc.enable_breakdown_service:
                        self.check_quotation_visibility = True
                        self.state = 'waiting'
                    elif self.service_type == 'routine' and not amc.enable_routine_maintenance:
                        self.check_quotation_visibility = True
                        self.state = 'waiting'
                    else:
                        self.check_quotation_visibility = False
                        self.state = 'draft'
        if show_warning:
            warning_mess = {
                'title': _('Remove the Following Products from Spare Parts'),
                'message': message
            }
            return {'warning': warning_mess}

    def service_approve(self):
        """This is the approve function of the service which create invoice
        corresponding to the service and the cost defined in amc will update
        if any running amc related to the corresponding customer"""
        if self.gen_sale_order_id.allocated_no_service != 0:
            self.gen_sale_order_id.remaining_no_service = self.gen_sale_order_id.remaining_no_service - 1
        else:
            raise UserError("There are no services left for the selected sale order")
        self.sudo().write({
            'state': 'approve'
        })

    def service_reject(self):
        """This is the reject function of the service
        which sends the corresponding record to the rejected list"""
        self.ensure_one()
        self.sudo().write({
            'state': 'reject'
        })
        return

    def action_view_material_request(self):
        """ View the related Material Request of the Service.
        """
        return {
            'name': _('Material Request'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'generator.material.request',
            'domain': [('pending_list_id', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }

    def unlink(self):
        state_list = ['waiting', 'draft']
        for rec in self:
            if rec.state not in state_list:
                raise UserError("You cannot delete the record at this state")
            if rec.state in state_list:
                rec.generator_service_picking_id.unlink()
            res = super(GeneratorService, self).unlink()
            return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_ids = fields.Many2many('sale.order')

    def action_post(self):
        """Here the post function of the invoice is inherited for changing
        the state of the service corresponding to the invoice to invoiced"""
        result = super(AccountMove, self).action_post()
        for sale_id in self.sale_order_ids:
            generator_service = self.env['generator.service'].search([('gen_sale_order_id', '=', sale_id.id)])
            contract_amount = generator_service.amc_contract_id.contract_amount
            generator_service.amc_contract_id.contract_amount = contract_amount - sale_id.amount_total
        return result


class ServiceTechnician(models.Model):
    _name = 'technician.details.line'
    _description = 'Technician Details'

    service_technician_id = fields.Many2one('generator.service')
    technician_id = fields.Many2one('hr.employee', string='Technician')
    service_technician_mobile = fields.Char(string='Mobile', related='technician_id.work_phone')


class StockMove(models.Model):
    _inherit = 'stock.move'

    service_generator_spare_parts_cost = fields.Float(string="Price")
    generator_spare_move_id = fields.Many2one('generator.service', string="Generator Reference")
