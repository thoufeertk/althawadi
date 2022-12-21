# -*- coding: utf-8 -*-
import xml.etree.ElementTree as xee

from odoo import fields, api, models


class Partner(models.Model):
    _inherit = 'res.partner'

    is_generator_customer = fields.Boolean(string='Generator Customer')
    generator_id = fields.Many2many('product.product', string='Generator',
                                    domain="[('is_generator', '=', True)]")
    # generator_id = fields.Many2many('product.product', string='Generator',
    #                                 domain="[('is_generator', '=', True),('type', '=','service')]")
    engine_fsd_number = fields.Char(string='Engine FSD Number')
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
    generator_spare_parts_ids = fields.One2many('contact.generator.spare.line', 'spare_parts_id')
    enable_routine_maintenance = fields.Boolean(string='Routine Maintenance')
    enable_monitor_service = fields.Boolean(string='Monitor Service')
    enable_deployment_service = fields.Boolean(string='Deployment Service')
    enable_breakdown_service = fields.Boolean(string='Break Down Service')
    gen_service_visual_rust = fields.Boolean(string='R-Visual Inspection for Rust')
    gen_service_check_any_deposition = fields.Boolean(string='Check Any Deposition (Oil, diesel, dust)')
    gen_service_check_any_cleanliness = fields.Boolean(string='Check the Cleanliness of the generator set')
    lub_service_lube_oil_level = fields.Boolean(string='Check for oil level')
    lub_service_lube_engine_oil_level = fields.Boolean(string='Check engine oil level')
    lub_service_lube_engine_oil_condition = fields.Boolean(string='Check engine oil condition')
    lub_service_lube_oil_filter = fields.Boolean(string='Check Oil filter')
    lub_service_lube_governer_oil = fields.Boolean(string='Check Governer Oil')
    lub_service_lube_oil_pressure = fields.Boolean(string='Check & record oil pressure')
    lub_service_hydraulic_governor_pressure = fields.Boolean(string='R-Check hydraulic governor oil level')
    fuel_service_leaks = fields.Boolean(string='Check for fuel leaks')
    fuel_service_main_tank_level = fields.Boolean(string='Check main tank level (S.S)')
    fuel_service_day_tank_level = fields.Boolean(string='Check day tank level (S.S)')
    fuel_service_transfer_pump = fields.Boolean(string='Check fuel transfer pump')
    fuel_service_drain_sediment = fields.Boolean(string='Drain sediments from tank (S.S)')
    fuel_service_governor_linkage = fields.Boolean(string='Check governor & linkage to pump')
    fuel_service_lines_connection = fields.Boolean(string='Check fuel lines & connection')
    fuel_service_filter = fields.Boolean(string='Check fuel filter')
    engine_service_unusual_vibration = fields.Boolean(string='Check engine unusual vibration')
    engine_service_mounting_hardware = fields.Boolean(string='Check engine tightening mounting hardware')
    cooling_service_coolant_leaks = fields.Boolean(string='Check coolant leaks')
    cooling_service_radiator_air_passageway = fields.Boolean(string='Check radiator air passageway for any restriction')
    cooling_service_hoses_connections = fields.Boolean(string='Check hoses & connections')
    cooling_service_coolant_level = fields.Boolean(string='Check Coolant level')
    cooling_service_belt_condition_tension = fields.Boolean(string='Check belt condition & tension')
    cooling_service_grease_leak = fields.Boolean(string='Check wobble & grease leak in fan Hub & drive pulley (S.S)')
    cooling_service_operation_heater = fields.Boolean(string='Check operation of Coolant heater')
    air_service_leaks = fields.Boolean(string='Check for Air Leaks')
    air_service_cleaner_passage = fields.Boolean(string='Check Air cleaner passageway for any restriction')
    air_service_piping_connection = fields.Boolean(string='Check piping & connections')
    electrical_service_battery = fields.Boolean(string='Check Check Battery')
    electrical_service_electrolyte = fields.Boolean(string='Check electrolyte level')
    electrical_service_gravity = fields.Boolean(string='Check specific gravity')
    electrical_service_charging_system = fields.Boolean(string='R-Check Charging system')
    electrical_service_load_breaker = fields.Boolean(string='R-Check Load breaker')
    generator_service_passage = fields.Boolean(string='Check air inlet & outlet passageway (Canopy/S.S louvers)')
    generator_service_control_panel = fields.Boolean(string='Check control panel lamps')
    starting_service_auto_manual = fields.Boolean(
        string="Start up the generator with selector switch set in auto/manual")
    starting_service_under_voltage = fields.Boolean(string="Check for under voltage")
    starting_service_terminal_voltage = fields.Boolean(string="Check and record terminal voltage")
    starting_service_frequency = fields.Boolean(string="Check and record Frequency")
    starting_service_load_current = fields.Boolean(string="Check load current (S.S)")
    starting_service_operation_total_hours = fields.Boolean(string="Service operation total hours")
    alarm_service_test_reset = fields.Boolean(string='Test and reset all alarms')
    alternator_service_insulation = fields.Boolean(string='Check & record alternator insulation resistance (IR)')
    select_all = fields.Boolean(string='Select All')

    @api.onchange('select_all')
    def _onchange_select_all(self):
        view_id = self.env.ref('generator_service_maintenance.res_partner_form_view_inherited')
        view_arch = str(view_id.arch_base)
        doc = xee.fromstring(view_arch)
        field_list = []
        for tag in doc.findall('.//field'):
            field_list.append(tag.attrib['name'])
        try:
            field_list.remove('select_all')
            field_list.remove('is_generator_customer')
        except:
            pass
        boolean_fields = self.env['ir.model.fields'].search(
            [('model_id.model', '=', 'res.partner'), ('ttype', '=', 'boolean'), ('name', 'in', field_list)])
        if self.select_all:
            for field in boolean_fields:
                self.update({field.name: True})
        else:
            for field in boolean_fields:
                self.update({field.name: False})

    # @api.onchange('generator_id')
    # def _onchange_generator_id(self):
    #     """In this onchange function of the generator_id loads the details
    #     of the generator to the partner form including spare parts details"""
    #     self.engine_fsd_number = self.generator_id.engine_fsd_number
    #     self.generator_image = self.generator_id.generator_image
    #     self.generator_serial_number = self.generator_id.generator_serial_number
    #     self.generator_kva_ph = self.generator_id.generator_kva_ph
    #     self.engine_serial_number = self.generator_id.engine_serial_number
    #     self.engine_model = self.generator_id.engine_model
    #     self.alternator_serial_number = self.generator_id.alternator_serial_number
    #     self.alternator_frame_size = self.generator_id.alternator_frame_size
    #     self.panel_amf = self.generator_id.panel_amf
    #     self.panel_amf_make = self.generator_id.panel_amf_make
    #     self.last_hours = self.generator_id.last_hours
    #     if self.generator_id.generator_spare_parts_ids:
    #         spare_parts_list = []
    #         self.generator_spare_parts_ids = [(5, 0, 0)]
    #         for spare_part_id in self.generator_id.generator_spare_parts_ids:
    #             vals = (0, 0, {
    #                 'generator_spare_parts': spare_part_id.generator_spare_parts.id,
    #                 'generator_spare_parts_quantity': spare_part_id.generator_spare_parts_quantity,
    #                 'generator_spare_parts_uom': spare_part_id.generator_spare_parts_uom.id,
    #                 'generator_spare_parts_cost': spare_part_id.generator_spare_parts_cost,
    #             })
    #             spare_parts_list.append(vals)
    #         self.update({'generator_spare_parts_ids': spare_parts_list})

    def button_quotation(self):
        """In this button function we can see the quotations related to the
        corresponding partner"""
        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'service.quotation',
            'domain': [('service_customer', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    def button_service(self):
        """In this button function we can see the services related to the
        corresponding partner"""
        return {
            'name': 'Service',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'generator.service',
            'domain': [('service_customer', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }


class GeneratorSpareLine(models.Model):
    _name = "contact.generator.spare.line"
    _description = 'Contract generator spare line'

    spare_parts_id = fields.Many2one('res.partner')
    generator_spare_parts = fields.Many2one('product.product', string="Spares")
    generator_spare_parts_quantity = fields.Float(string='Quantity', default=1.0)
    generator_spare_parts_uom = fields.Many2one('uom.uom', string='Unit')
    generator_spare_parts_cost = fields.Float(string="Unit Price")

    @api.onchange('generator_spare_parts')
    def onchange_generator_spare_parts(self):
        """This is the onchange function for loading the unit of measurement
        and cost defined in the product form to the spare parts line"""
        self.generator_spare_parts_uom = self.generator_spare_parts.uom_id
        self.generator_spare_parts_cost = self.generator_spare_parts.standard_price
