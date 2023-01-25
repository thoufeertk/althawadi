"""Initial Inspection"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InitialInspection(models.Model):
    """Initial Inspection"""
    _name = 'initial.inspection'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "Initial Inspection"

    enquiry_number = fields.Many2one('enquiry.register', string="Pending Enquiry List", copy=False,
                                     domain=[('state', '=', 'pending')])
    name = fields.Char(string="Enquiry reference number", copy=False)
    customer_name = fields.Many2one('res.partner', string="Customer Name",
                                    domain=[("customer_rank", ">", 0)], required=1)
    service_priority = fields.Selection([('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
                                        default='high', string="Service Priority")
    service_deadline = fields.Date(string="Service deadline", required=1)
    machine_type = fields.Many2one('product.product', string="Type of Machine", required=1,
                                   domain=[('is_machine', '=', True)])
    quantity = fields.Float(string="Quantity")
    repair_reason = fields.Text(string="Customer reason for repair")
    # machine details
    category = fields.Many2one('machine.type', string="Machine Type/Category")
    made = fields.Char(string="Made")
    make = fields.Char(string="Make")
    kilo = fields.Char(string="Kilowatt (KW)")
    kva = fields.Char(string="KVA")
    horsepower = fields.Char(string="Horsepower")
    machine_serial_number = fields.Char(string="Serial Number")
    item_code = fields.Char(string="Item Code")
    rpm = fields.Char(string="RPM")
    pole = fields.Char(string="Pole")
    volt = fields.Char(string="Volts")
    amps = fields.Char(string="Amps")
    hertz = fields.Char(string="Hertz")
    motor_no = fields.Char(string="Motor No.")
    # service cost estimation fields
    parts_required = fields.One2many('required.parts', 'inspection_part_link',
                                     string="Parts Required")
    services = fields.One2many('workshop.services', 'service_inspection', string="Services")
    other_cost_information = fields.One2many('other.charges', 'initial_inspection_id')
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('done', 'Done')],
                             default='draft', readonly=True)
    # fields for counting the number of records of mechanical report and work order
    mechanical_count = fields.Integer(compute='_compute_mechanical_count')
    order_count = fields.Integer(compute='_compute_order_count')
    # field for checking the current loaded customer have amc or not
    amc_customer = fields.Boolean(string="Amc Customer", compute='check_customer_name')
    # relational field of amc contract
    contract_id = fields.Many2one('workshop.contract')
    contract_amount = fields.Float(related='contract_id.contract_amount')
    total_service_cost = fields.Float(string='Service Cost', compute='_compute_amounts')
    total_parts_cost = fields.Float(string='Parts Cost', compute='_compute_amounts')
    total_other_cost = fields.Float(string='Other Cost', compute='_compute_amounts')
    # total cost including service,parts and other cost
    work_price = fields.Float(string="Estimated Cost", compute='_compute_amounts')

    @api.depends('services', 'parts_required', 'other_cost_information')
    def _compute_amounts(self):
        service_cost_list = []
        parts_cost_list = []
        other_cost_list = []
        for service in self.services:
            service_cost_list.append(service.cost)
        for parts in self.parts_required:
            parts_cost_list.append(parts.cost)
        for other in self.other_cost_information:
            other_cost_list.append(other.charge_cost)
        self.total_service_cost = sum(service_cost_list)
        self.total_parts_cost = sum(parts_cost_list)
        self.total_other_cost = sum(other_cost_list)
        self.work_price = self.total_service_cost + self.total_parts_cost + self.total_other_cost

    def _get_default_currency_id(self):
        """gets company currency"""
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id)

    @api.depends('customer_name', 'service_deadline')
    def check_customer_name(self):
        """checks if customer has a running contract"""
        contract = self.env['workshop.contract']
        customer = self.customer_name.id
        deadline = self.service_deadline
        running_contract = contract.search([('contract_partner_id', '=', customer),
                                            ('state', '=', 'running'),
                                            ('contract_start_date', '<=', deadline),
                                            ('contract_end_date', '>=', deadline)
                                            ], limit=1)
        if running_contract:
            self.amc_customer = True
            self.contract_id = running_contract.id
            # self.machine_type = running_contract.machine.id
        else:
            self.amc_customer = False

    def _compute_mechanical_count(self):
        """coounts mechanical reports created from this inspection"""
        self.mechanical_count = self.env['mechanical.report'].search_count(
            [('job_no', '=', self.id)]) or 0

    def _compute_order_count(self):
        """coounts mechanical reports created from this inspection"""
        self.order_count = self.env['workshop.order'].search_count(
            [('initial_inspection', '=', self.id)]) or 0

    def validate(self):
        """Adds sequence code to each record while creating it"""
        self.state = 'pending'
        self.enquiry_number.state = 'done'
        sequence = self.env['ir.sequence']
        self.name = sequence.next_by_code('initial.inspection.code') or _('New')

    @api.model
    def create(self, vals):
        """Sets sequence code to '/'"""
        vals['name'] = '/'
        return super(InitialInspection, self).create(vals)

    def unlink(self):
        """restricts deletion of record once number is generated"""
        for move in self:
            if move.name != '/' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been validated once."))
        return super(InitialInspection, self).unlink()

    # @api.onchange('machine_type')
    # def machine_details(self):
    #     """updates machine details"""
    #     self.parts_required = None
    #     self.services = None
    #     data = ['made', 'make', 'kilo', 'kva', 'horsepower', 'machine_serial_number', 'rpm', 'item_code',
    #             'pole', 'volt', 'amps', 'hertz', 'motor_no']
    #     no_value = {
    #         'made': "", 'make': "", 'kilo': "", 'kva': "", 'horsepower': "", 'machine_serial_number': "", 'rpm': "",
    #         'item_code': "",
    #         'pole': "", 'volt': "", 'amps': "", 'hertz': "", 'motor_no': "",
    #         'category': ""
    #     }
    #     self.update(no_value)
        # if self.machine_type:
        #     # machine_details = self.machine_type.read(data)[0]
        #     # self.category = self.machine_type.category.id
        #     # machine_details.pop('id')
        #     # self.update(machine_details)
        #     # data = ['product_id', 'quantity', 'product_unit', 'cost']
        #     # if self.amc_customer:
        #     #     parts = self.contract_id.m_parts_required.filtered(
        #     #         lambda l: l.contract_sale_product.id == self.machine_type.id).read(data)
        #     # else:
        #     #     parts = self.machine_type.m_parts_required.read(data)
        #     # for part in parts:
        #     #     for item in part:
        #     #         if isinstance(part[item], tuple):
        #     #             part[item] = part[item][0]
        #     #     part.pop('id')
        #     #     self.parts_required |= self.parts_required.new(part)
        #     data = ['mechanical_works', 'cost', 'total_hours']
        #     # if self.amc_customer:
        #     #     services = self.contract_id.service_required.filtered(
        #     #         lambda l: l.contract_sale_product.id == self.machine_type.id).read(data)
        #     # else:
        #     #     services = self.machine_type.service_required.read(data)
        #     # for service in services:
        #     #     for item in service:
        #     #         if isinstance(service[item], tuple):
        #     #             service[item] = service[item][0]
        #     #     service.pop('id')
        #     #     self.services |= self.services.new(service)

    def mechanical_report(self):
        """creates mechanical report"""

        # data = [ 'item_code', 'machine_serial_number', 'rpm', 'pole', 'volt', 'amps',
        #         'hertz',
        #         'motor_no']
        # machine_details = self.machine_type.read(data)[0]
        # machine_details.pop('id')
        machine_details = {}
        # for data in machine_details:
        #     if isinstance(machine_details[data], tuple):
        #         machine_details[data] = machine_details[data][0]
        machine_details['customer_name'] = self.customer_name.id
        machine_details['machine_type'] = self.machine_type.id
        machine_details['quantity'] = self.quantity
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
        machine_details['item_code'] = self.item_code
        machine_details['motor_no'] = self.motor_no
        machine_details['make'] = self.make
        machine_details['job_no'] = self.id
        report = self.env['mechanical.report'].create(machine_details)
        return {
            'name': 'Mechanical Report',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mechanical.report',
            'res_id': report.id,
            'target': 'current'
        }

    def button_mechanical(self):
        """views linked mechanical reports"""
        return {
            'name': 'Mechanical Report',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mechanical.report',
            'domain': [('job_no', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    def button_workorder(self):
        """views linked work orders"""
        return {
            'name': 'Work Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'workshop.order',
            'domain': [('initial_inspection', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    @api.onchange('enquiry_number')
    def onchange_enquiry(self):
        """fill enquiry data"""
        if self.enquiry_number:
            data = ['customer_name', 'service_priority',
                    'service_deadline', 'machine_type', 'repair_reason']
            values = self.enquiry_number.read(data)[0]
            values.pop('id')
            for data in values:
                if isinstance(values[data], tuple):
                    values[data] = values[data][0]
            self.update(values)

