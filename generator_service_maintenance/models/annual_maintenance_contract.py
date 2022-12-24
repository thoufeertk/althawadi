# -*- coding: utf-8 -*-
from datetime import date, datetime

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AnnualMaintenanceContract(models.Model):
    _name = "annual.maintenance.contract"
    _rec_name = "name"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Annual Maintenance Contract'

    contract_partner_id = fields.Many2one('res.partner', string="Customer",
                                          domain="[('is_generator_customer', '=', True)]", required=True)
    contract_start_date = fields.Date(required=1)
    contract_end_date = fields.Date(required=1)
    contract_amount = fields.Float(string='AMC amount', required=1)
    contract_generator_name = fields.Char(string='Generator Name')
    contract_generator_image = fields.Binary()
    contract_generator_serial_number = fields.Char()
    contract_generator_kva_ph = fields.Char()
    contract_engine_serial_number = fields.Char()
    contract_engine_model = fields.Char()
    contract_alternator_serial_number = fields.Char()
    contract_alternator_frame_size = fields.Char()
    contract_panel_amf = fields.Char()
    contract_panel_amf_make = fields.Char()
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('running', 'Running'),
        ('reject', 'Rejected'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', copy=False, track_visibility='onchange')
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    generator_id = fields.Many2one('product.product', string='Generator', domain="[('is_generator', '=', True)]")
    engine_fsd_number = fields.Char(string='Generator Name', related='generator_id.engine_fsd_number',
                                    readonly=False)
    generator_image = fields.Binary()
    generator_serial_number = fields.Char(string='Generator Serial No',
                                          related='generator_id.generator_serial_number', readonly=False)
    generator_kva_ph = fields.Char(string='Generator KVA/PH', related='generator_id.generator_kva_ph',
                                   readonly=False)
    engine_serial_number = fields.Char(string='Engine Serial No', related='generator_id.engine_serial_number',
                                       readonly=False)
    engine_model = fields.Char(string='Engine Model', related='generator_id.engine_model', readonly=False)
    alternator_serial_number = fields.Char(string='Alternator Serial Number',
                                           related='generator_id.alternator_serial_number', readonly=False)
    alternator_frame_size = fields.Char(string='Alternator Frame Size',
                                        related='generator_id.alternator_frame_size', readonly=False)
    panel_amf = fields.Char(string='Panel - AMF/Manual (PIU)',
                            related='generator_id.panel_amf', readonly=False)
    panel_amf_make = fields.Char(string='AMF Panel / PIU Make',
                                 related='generator_id.panel_amf_make', readonly=False)
    last_hours = fields.Char(string='Last Serv.Hours & Date',
                             related='generator_id.last_hours', readonly=False)
    generator_spare_parts_ids = fields.One2many('generator.spare.line', 'spare_parts_id',
                                                related='generator_id.generator_spare_parts_ids')
    enable_monitor_service = fields.Boolean(string='Monitor Service',
                                            related='contract_partner_id.enable_monitor_service')
    enable_routine_maintenance = fields.Boolean(string='Routine Maintenance',
                                                related='contract_partner_id.enable_routine_maintenance')
    enable_deployment_service = fields.Boolean(string='Deployment Service',
                                               related='contract_partner_id.enable_deployment_service')
    enable_breakdown_service = fields.Boolean(string='Break Down Service',
                                              related='contract_partner_id.enable_breakdown_service')
    gen_service_visual_rust = fields.Boolean(string='R-Visual Inspection for Rust',
                                             related='contract_partner_id.gen_service_visual_rust')
    gen_service_check_any_deposition = fields.Boolean(string='Check Any Deposition (Oil, diesel, dust)',
                                                      related='contract_partner_id.gen_service_check_any_deposition')
    gen_service_check_any_cleanliness = fields.Boolean(string='Check the Cleanliness of the generator set',
                                                       related='contract_partner_id.gen_service_check_any_cleanliness')
    lub_service_lube_oil_level = fields.Boolean(string='Check for oil level',
                                                related='contract_partner_id.lub_service_lube_oil_level')
    lub_service_lube_engine_oil_level = fields.Boolean(string='Check engine oil level',
                                                       related='contract_partner_id.lub_service_lube_engine_oil_level')
    lub_service_lube_engine_oil_condition = fields.Boolean(string='Check engine oil condition',
                                                           related='contract_partner_id'
                                                                   '.lub_service_lube_engine_oil_condition')
    lub_service_lube_oil_filter = fields.Boolean(string='Check Oil filter',
                                                 related='contract_partner_id.lub_service_lube_oil_filter')
    lub_service_lube_governer_oil = fields.Boolean(string='Check Governer Oil',
                                                   related='contract_partner_id.lub_service_lube_governer_oil')
    lub_service_lube_oil_pressure = fields.Boolean(string='Check & record oil pressure',
                                                   related='contract_partner_id.lub_service_lube_oil_pressure')
    lub_service_hydraulic_governor_pressure = fields.Boolean(string='R-Check hydraulic governor oil level',
                                                             related='contract_partner_id'
                                                                     '.lub_service_hydraulic_governor_pressure')
    fuel_service_leaks = fields.Boolean(string='Check for fuel leaks', related='contract_partner_id.fuel_service_leaks')
    fuel_service_main_tank_level = fields.Boolean(string='Check main tank level (S.S)',
                                                  related='contract_partner_id.fuel_service_main_tank_level')
    fuel_service_day_tank_level = fields.Boolean(string='Check day tank level (S.S)',
                                                 related='contract_partner_id.fuel_service_day_tank_level')
    fuel_service_transfer_pump = fields.Boolean(string='Check fuel transfer pump',
                                                related='contract_partner_id.fuel_service_transfer_pump')
    fuel_service_drain_sediment = fields.Boolean(string='Drain sediments from tank (S.S)',
                                                 related='contract_partner_id.fuel_service_drain_sediment')
    fuel_service_governor_linkage = fields.Boolean(string='Check governor & linkage to pump',
                                                   related='contract_partner_id.fuel_service_governor_linkage')
    fuel_service_lines_connection = fields.Boolean(string='Check fuel lines & connection',
                                                   related='contract_partner_id.fuel_service_lines_connection')
    fuel_service_filter = fields.Boolean(string='Check fuel filter', related='contract_partner_id.fuel_service_filter')
    engine_service_unusual_vibration = fields.Boolean(string='Check engine unusual vibration',
                                                      related='contract_partner_id.engine_service_unusual_vibration')
    engine_service_mounting_hardware = fields.Boolean(string='Check engine tightening mounting hardware',
                                                      related='contract_partner_id.engine_service_mounting_hardware')
    cooling_service_coolant_leaks = fields.Boolean(string='Check coolant leaks',
                                                   related='contract_partner_id.cooling_service_coolant_leaks')
    cooling_service_radiator_air_passageway = fields.Boolean(string='Check radiator air passageway for any restriction',
                                                             related='contract_partner_id'
                                                                     '.cooling_service_radiator_air_passageway')
    cooling_service_hoses_connections = fields.Boolean(string='Check hoses & connections',
                                                       related='contract_partner_id.cooling_service_hoses_connections')
    cooling_service_coolant_level = fields.Boolean(string='Check Coolant level',
                                                   related='contract_partner_id.cooling_service_coolant_level')
    cooling_service_belt_condition_tension = fields.Boolean(string='Check belt condition & tension',
                                                            related='contract_partner_id'
                                                                    '.cooling_service_belt_condition_tension')
    cooling_service_grease_leak = fields.Boolean(string='Check wobble & grease leak in fan Hub & drive pulley (S.S)',
                                                 related='contract_partner_id.cooling_service_grease_leak')
    cooling_service_operation_heater = fields.Boolean(string='Check operation of Coolant heater',
                                                      related='contract_partner_id.cooling_service_operation_heater')
    air_service_leaks = fields.Boolean(string='Check for Air Leaks', related='contract_partner_id.air_service_leaks')
    air_service_cleaner_passage = fields.Boolean(string='Check Air cleaner passageway for any restriction',
                                                 related='contract_partner_id.air_service_cleaner_passage')
    air_service_piping_connection = fields.Boolean(string='Check piping & connections',
                                                   related='contract_partner_id.air_service_piping_connection')
    electrical_service_battery = fields.Boolean(string='Check Check Battery',
                                                related='contract_partner_id.electrical_service_battery')
    electrical_service_electrolyte = fields.Boolean(string='Check electrolyte level',
                                                    related='contract_partner_id.electrical_service_electrolyte')
    electrical_service_gravity = fields.Boolean(string='Check specific gravity',
                                                related='contract_partner_id.electrical_service_gravity')
    electrical_service_charging_system = fields.Boolean(string='R-Check Charging system',
                                                        related='contract_partner_id.electrical_service_charging_system')
    electrical_service_load_breaker = fields.Boolean(string='R-Check Load breaker',
                                                     related='contract_partner_id.electrical_service_load_breaker')
    generator_service_passage = fields.Boolean(string='Check air inlet & outlet passageway (Canopy/S.S louvers)',
                                               related='contract_partner_id.generator_service_passage')
    generator_service_control_panel = fields.Boolean(string='Check control panel lamps',
                                                     related='contract_partner_id.generator_service_control_panel')
    starting_service_auto_manual = fields.Boolean(
        string="Start up the generator with selector switch set in auto/manual",
        related='contract_partner_id.starting_service_auto_manual')
    starting_service_under_voltage = fields.Boolean(string="Check for under voltage",
                                                    related='contract_partner_id.starting_service_under_voltage')
    starting_service_terminal_voltage = fields.Boolean(string="Check and record terminal voltage",
                                                       related='contract_partner_id.starting_service_terminal_voltage')
    starting_service_frequency = fields.Boolean(string="Check and record Frequency",
                                                related='contract_partner_id.starting_service_frequency')
    starting_service_load_current = fields.Boolean(string="Check load current (S.S)",
                                                   related='contract_partner_id.starting_service_load_current')
    starting_service_operation_total_hours = fields.Boolean(string="Service Operation Total Hours",
                                                            related='contract_partner_id'
                                                                    '.starting_service_operation_total_hours')
    alarm_service_test_reset = fields.Boolean(string='Test and reset all alarms',
                                              related='contract_partner_id.alarm_service_test_reset')
    alternator_service_insulation = fields.Boolean(string='Check & record alternator insulation resistance (IR)',
                                                   related='contract_partner_id.alternator_service_insulation')
    cust_purchase_order_no = fields.Char(string='Buyers Order No.')
    contract_order_no = fields.Char(string='Contract Order Number')

    @api.onchange('contract_partner_id')
    def _onchange_contract_partner_id(self):
        if self.contract_partner_id:
            domain = {'domain': {'generator_id': [('id', 'in', self.contract_partner_id.generator_id.ids)]}}
            return domain

    def action_submit(self):
        """This is the submit function of the amc which changes the state of the record to
        submit"""
        self.name = self.env['ir.sequence'].next_by_code('annual.maintenance.contract')
        self.sudo().write({
            'state': 'submit'
        })

    def action_approve(self):
        """This is the approve function which changes the state to running"""
        self.sudo().write({
            'state': 'running'
        })

    def action_reject(self):
        """This is the reject function which send the corresponding record to the
        rejected list"""
        self.sudo().write({
            'state': 'reject'
        })

    def service_expired(self):
        """This is a cron function which is used to check the validity of the
        annual maintenance contract"""
        doc_ids = self.search([])
        for rec in doc_ids:
            if rec.contract_end_date < date.today():
                rec.sudo().write({
                    'state': 'expired'
                })

    def unlink(self):
        state_list = ['running']
        for annual_contract in self:
            if annual_contract.state in state_list:
                raise UserError("You cannot delete the record at this state")
        res = super(AnnualMaintenanceContract, self).unlink()
        return res

    def calculate_expiration(self):
        annual_maintenance_contracts = self.env['annual.maintenance.contract'].search([('state', '=', 'running')])
        current_date = datetime.today().date()
        settings_maintenance_days = self.env['ir.config_parameter'].sudo().get_param(
            'contract_maintenance_date') or ''
        settings_maintenance_amount = self.env['ir.config_parameter'].sudo().get_param(
            'contract_maintenance_amount') or ''
        if annual_maintenance_contracts:
            for maintenance_contract in annual_maintenance_contracts:
                date_interval = maintenance_contract.contract_end_date - current_date
                if int(date_interval.days) <= int(settings_maintenance_days):
                    values = {
                        'mail': maintenance_contract.contract_partner_id.email,
                        'name': maintenance_contract.contract_partner_id.name,
                        'content': "is expired before :" + str(date_interval.days) +
                                   "Days",
                    }
                    self.send_mail(values)
                if int(maintenance_contract.contract_amount) <= int(settings_maintenance_amount):
                    values = {
                        'mail': maintenance_contract.contract_partner_id.email,
                        'name': maintenance_contract.contract_partner_id.name,
                        'content': " is expired now . So Kindly update your AMC contract price is below " + str(
                            settings_maintenance_amount) + " Now your AMC Balance is" + str(
                            maintenance_contract.contract_amount),
                    }
                    self.send_mail(values)

    def send_mail(self, values):
        """ This function for assign values to the template for send AMC Contract expire """
        body = """<table border="0" width="100%" cellpadding="0" bgcolor="#ededed" style="padding: 20px; background-color: #ededed; border-collapse:separate;" summary="o_mail_notification">
                                                    <tbody>
                                                        <!-- HEADER -->
                                                        <tr>
                                                            <td align="center" style="min-width: 590px;">
                                                                <table width="590" border="0" cellpadding="0" bgcolor="#875A7B" style="min-width: 590px; background-color: rgb(135,90,123); padding: 20px; border-collapse:separate;">
                                                                    <tr>
                                                                        <td valign="middle">
                                                                            <span style="font-size:20px; color:white; font-weight: bold;">
                                                                                AWC Expire Reminder
                                                                            </span>
                                                                        </td>
                                                                    </tr>
                                                              </table>
                                                        </td>
                                                      </tr>
                                                      <!-- CONTENT -->
                                                      <tr>
                                                            <td align="center" style="min-width: 590px;">
                                                                <table width="590" border="0" cellpadding="0" bgcolor="#ffffff" style="min-width: 590px; background-color: rgb(255, 255, 255); padding: 20px; border-collapse:separate;">
                                                                    <tbody>
                                                                        <td valign="top" style="font-family:Arial,Helvetica,sans-serif; color: #555; font-size: 14px;">
                                                                            <p>Dear""""  " + values['name'] + """,</p>
                                                                            <p>Your AMC Contract""" + values[
            'content'] + """
                                                                            </p>
                                                                            <p>Thank you</p>
                                                                            <p style="color:#888888">
                                                                        </td>
                                                                    </tbody>
                                                                </table>
                                                            </td>
                                                        </tr>
                                                        <!-- FOOTER -->
                                                        <tr>
                                                            <td align="center" style="min-width: 590px;">
                                                                <table width="590" border="0" cellpadding="0" bgcolor="#875A7B" style="min-width: 590px; background-color: rgb(135,90,123); padding: 20px; border-collapse:separate;">
                                                                    <tr>

                                                                    </tr>
                                                                </table>
                                                            </td>
                                                        </tr>
                                                        <tr>

                                                        </tr>
                                                    </tbody>
                                                    </table>"""
        main_content = {
            'subject': 'AMC Price List Reminder for ''   ' + values['name'],
            'body_html': body,
            'email_to': values['mail'],
        }
        self.env['mail.mail'].create(main_content).send()
