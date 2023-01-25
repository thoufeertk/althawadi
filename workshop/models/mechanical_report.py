from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MechanicalReport(models.Model):
    _name = 'mechanical.report'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Mechanical Report"

    customer_name = fields.Many2one('res.partner', string="Customer Name",
                                    domain=[("customer_rank", ">", 0)], required=1)
    report_date = fields.Date(string="Date", default=fields.Datetime.now)
    job_no = fields.Many2one('initial.inspection', string="Job Number", domain=[('state', '=', 'pending')])
    notification_no = fields.Char(string="Notification Number")
    motor_no = fields.Char(string="Motor Number")
    end_user = fields.Char(string="End User")
    machine_type = fields.Many2one('product.product', string="Type of Machine", domain=[('is_machine', '=', True)])
    overhauling = fields.Boolean(string="Overhauling")
    rewinding = fields.Boolean(string="Rewinding")
    horsepower = fields.Char(string="Horsepower")
    machine_serial_number = fields.Char(string="Serial Number")
    item_code = fields.Char(string="Item Code")
    pole = fields.Char(string="Pole")
    made = fields.Char(string="Made")
    item_code = fields.Char(string="Item Code")
    motor_no = fields.Char(string="Motor No.")
    make = fields.Char(string="Make")
    kilo = fields.Char(string="Kilowatt (KW)")
    kva = fields.Char(string="KVA")
    frame = fields.Char(string="Frame")
    volt = fields.Char(string="Volts")
    amps = fields.Char(string="Amps")
    rpm = fields.Char(string="RPM")
    hertz = fields.Char(string="Hertz")
    name = fields.Char(string="Name")
    quantity = fields.Float(string='Quantity')
    # stator data
    slots = fields.Integer(string="Number of Slots")
    core_length = fields.Float(string="Core Length")
    core_diameter = fields.Float(string="Core Diameter")
    groups_no = fields.Integer(string="No. of Groups")
    coils_group = fields.Integer(string="No. of Coils Per Group")
    turns = fields.Integer(string="No. of Turns")
    parallel_wires = fields.Integer(string="No. of Wires in Parellel")
    connection_overhang = fields.Float(string="Connection Overhang")
    non_connection_end_overhang = fields.Float(string="Non Conn. End Overhang")
    pitch = fields.Float(string="Pitch")
    wire_size = fields.Float(string="Wire Size")

    changed_to = fields.Char(string="Changed to")
    winding_taken_by = fields.Char(string="Winding Data Taken By")
    # fan data
    fan_type = fields.Char(string="Fan Type")
    blades_no = fields.Integer(string="No. of Blades")
    fan_key_size = fields.Char(string="Fan Key Size")
    # End Cover Data
    end_cover_de = fields.Char(string="D.E")
    end_cover_nde = fields.Char(string="N.D.E")
    oil_seed_de = fields.Char(string="Oil Seal Size D.E")
    oil_seed_nde = fields.Char(string="Oil Seal Size N.D.E")
    wave_spring = fields.Char(string="Wave Spring")
    # Bearing Data
    bearing_de_no = fields.Char(string="D.E No.")
    bearing_nde_no = fields.Char(string="N.D.E No.")
    # Clearance & Fits
    shaft_de_cover = fields.Char(string="Shaft with D.E cover bore")
    shaft_nde_cover = fields.Char(string="Shaft with N.D.E cover bore")
    # Rotor Data
    rotor_bars = fields.Char(string="No. of Bars & Type")
    rotor_dia = fields.Char(string="Rotor Diameter")
    shaft_length = fields.Char(string="Shaft Length")
    no_of_steps = fields.Char(string="No. of Steps")
    de_journal_dia = fields.Char(string="D.E. Journal Diameter")
    nde_journal_dia = fields.Char(string="N.D.E. Journal Diameter")
    # Coupling & Pulley
    coupling_pully = fields.Char(string="Coupling & Pulley Type")
    coupling_bore = fields.Char(string="Coupling/Pulley bore size")
    coupling_key_size = fields.Char(string="Coupling Key Size")
    defects = fields.Char(string="Defects Noted Vide Visual")

    inspection_by = fields.Char(string="Inspection & Checking Carried Out :")
    other_by = fields.Char(string="Other Data Taken By :")
    action_todo = fields.Text(string="Action Proposed")
    mechanical_inspection_by = fields.Char(string="Mechanical Inspection Carried Out By :")
    quotation_count = fields.Integer(compute='_compute_quotation_count')
    amc_customer = fields.Boolean(string="Amc Customer", related='job_no.amc_customer')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('work_order', 'Work Order'),
        ('quotation', 'Quotation'),
    ], default='draft', readonly=True)

    def _compute_quotation_count(self):
        self.quotation_count = self.env['workshop.quotation'].search_count(
            [('pending_enquiry', '=', self.job_no.id)]) or 0

    def validate(self):
        """Adds sequence code to each record while creating it"""
        self.state = 'validated'
        sequence = self.env['ir.sequence']
        self.name = sequence.next_by_code('mechanical.report.code') or _('New')

    @api.model
    def create(self, vals):
        vals['name'] = '/'
        return super(MechanicalReport, self).create(vals)

    def unlink(self):
        """restricts deletion of record once number is generated"""
        for move in self:
            if move.name != '/' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been validated once."))
        return super(MechanicalReport, self).unlink()

    # @api.onchange('machine_type')
    # def onchange_machine_type(self):
    #     if self.machine_type:
    #         machine_details = \
    #             self.machine_type.read(['kilo', 'kva', 'horsepower', 'machine_serial_number', 'item_code', 'rpm',
    #                                     'pole', 'volt', 'amps', 'hertz', 'motor_no'])[0]
    #         machine_details.pop('id')
    #         self.update(machine_details)

    def create_quotation(self):
        if self.machine_type:
            # machine_details = self.machine_type.read(
            #     ['kilo', 'kva', 'horsepower', 'machine_serial_number', 'item_code', 'rpm', 'made', 'make',
            #      'pole', 'volt', 'amps', 'hertz', 'motor_no'])[0]
            # machine_details.pop('id')
            machine_details = {}
            customer_details = self.customer_name.read(['street', 'street2', 'city', 'state_id', 'zip', 'country_id'])[
                0]
            customer_details.pop('id')
            for data in customer_details:
                if type(customer_details[data]) == tuple:
                    customer_details[data] = customer_details[data][0]
            customer_details['customer_name'] = self.customer_name.id
            customer_details['machine_id'] = self.machine_type.id
            customer_details['pending_enquiry'] = self.job_no.id
            customer_details['quantity'] = self.quantity
            # customer_details['price'] = self.job_no.work_price
            machine_details['horsepower'] = self.horsepower
            machine_details['machine_serial_number'] = self.machine_serial_number
            machine_details['item_code'] = self.item_code
            machine_details['pole'] = self.pole
            machine_details['kilo'] = self.kilo
            machine_details['kva'] = self.kva
            machine_details['volt'] = self.volt
            machine_details['amps'] = self.amps
            machine_details['rpm'] = self.rpm
            machine_details['hertz'] = self.hertz
            machine_details['made'] = self.made
            machine_details['make'] = self.make
            machine_details['motor_no'] = self.motor_no
            machine_details.update(customer_details)
            quotation = self.env['workshop.quotation'].create(machine_details)
            quotation.onchange_pending_enquiry()
            quotation_parts = []
            quotation_services = []
            quotation_other = []
            quotation_line = []
            for line in self.job_no:
                description = []
                name_list = []
                if line.kilo:
                    name_list.append(line.machine_type.name)
                if line.kilo:
                    name_list.append(line.kilo + 'KW')
                if line.horsepower:
                    name_list.append(line.horsepower + 'HP')
                if line.pole:
                    name_list.append(line.pole + 'Pole')
                if line.rpm:
                    name_list.append(line.rpm + 'RPM')
                if line.kva:
                    name_list.append(line.kva + 'Kva')
                for service in line.services:
                    description.append(service.mechanical_works.name)
                name = '\n'.join(description)
                machine_rating = ', '.join(name_list)
                quotation_line.append([0, 0, {
                    'display_type': 'line_section',
                    'name': machine_rating,
                }])
                for service_line in self.job_no.services:
                    sale_line = {
                        'quotation_id': quotation.id,
                        'product_id': service_line.mechanical_works.id,
                        'name': service_line.mechanical_works.name,
                        'product_uom_qty': service_line.total_hours,
                        'price_unit': service_line.cost,
                        'product_uom': service_line.mechanical_works.uom_id.id,
                        'tax_id': service_line.mechanical_works.taxes_id.ids,
                    }
                    quotation_line.append((0, 0, sale_line))
            for parts_line in self.job_no.parts_required:
                sale_line = {
                    'product_id': parts_line.product_id.id,
                    'quantity': parts_line.quantity,
                    'product_unit': parts_line.product_unit.id,
                    'quotation_part_link': quotation.id,
                    'order_parts': parts_line.order_parts.id,
                    'm_parts_link': parts_line.m_parts_link.id,
                    'contract_parts': parts_line.contract_parts.id,
                    'cost': parts_line.cost,
                    'contract_sale_product': parts_line.contract_sale_product.id,
                }
                quotation_parts.append((0, 0, sale_line))
            for service_line in self.job_no.services:
                sale_line = {
                    'total_hours': service_line.total_hours,
                    'mechanical_works': service_line.mechanical_works.id,
                    'cost': service_line.cost,
                    'service_quotation': quotation.id,
                    'machine': service_line.machine.id,
                    'contract_machine': service_line.contract_machine.id,
                    'contract_sale_product': service_line.contract_sale_product.id,
                }
                quotation_services.append((0, 0, sale_line))
            for other_line in self.job_no.other_cost_information:
                sale_line = {
                    'work_quotation_id': quotation.id,
                    'charge_cost': other_line.charge_cost,
                    'charge_description': other_line.charge_description,
                }
                quotation_other.append((0, 0, sale_line))
            quotation.update({
                'parts_required': quotation_parts,
                'services': quotation_services,
                'other_cost_information': quotation_other,
                'work_quotation_line_ids': quotation_line,
            })
            self.state = 'quotation'
            return {
                'name': 'Quotation',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'workshop.quotation',
                'res_id': quotation.id,
                'target': 'current'
            }

    def button_quotation(self):
        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'workshop.quotation',
            'domain': [('pending_enquiry', '=', self.job_no.id)],
            'context': {'create': False},
            'target': 'current'
        }

    @api.onchange('job_no')
    def onchange_job_no(self):
        job = self.job_no
        if job:
            machine_details = \
                self.job_no.read(['kilo', 'kva', 'horsepower', 'machine_serial_number', 'item_code', 'rpm',
                                  'pole', 'volt', 'amps', 'hertz', 'motor_no'])[0]
            machine_details.pop('id')
            for data in machine_details:
                if type(machine_details[data]) == tuple:
                    machine_details[data] = machine_details[data][0]
            machine_details['customer_name'] = job.customer_name.id
            machine_details['machine_type'] = job.machine_type.id
            self.update(machine_details)

    def create_work_order(self):
        """creates workorder"""
        picking_type_id = self.env.ref('stock.picking_type_internal')
        location_id = picking_type_id.default_location_src_id.id
        destination_id = picking_type_id.default_location_dest_id.id
        if location_id and destination_id:
            picking_vals = {
                'partner_id': self.customer_name.id,
                'picking_type_id': picking_type_id.id,
                'location_id': location_id,
                'location_dest_id': destination_id,
            }
            picking_id = self.env['stock.picking'].sudo().create(picking_vals)

        work_order = self.env['workshop.order'].create({
            'customer_name': self.job_no.customer_name.id,
            'initial_inspection': self.job_no.id,
            'workshop_picking_id': picking_id.id if picking_id else None,
            'parts_required': [(0, 0, {
                'picking_type_id': picking_type_id.id,
                'picking_id': picking_id.id,
                'name': lines.product_id.name,
                'product_id': lines.product_id.id,
                'product_uom': lines.product_id.uom_id.id,
                'product_uom_qty': lines.quantity,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': lines.product_id.workshop_stock_location.id,
            }) for lines in self.job_no.parts_required]})
        self.state = 'work_order'
        work_order.customer_name = self.job_no.customer_name
        work_order.order_priority = self.job_no.service_priority
        self.job_no.state = 'done'

        return {
            'name': 'Work Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'workshop.order',
            'res_id': work_order.id,
            'target': 'current'
        }
