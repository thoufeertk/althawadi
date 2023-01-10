"""Workshop Quotation"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WorkshopQuotation(models.Model):
    """Workshop Quotation"""
    _name = 'workshop.quotation'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Quotation"

    pending_enquiry = fields.Many2one('initial.inspection', string="Pending List",
                                      domain=[('state', '=', 'pending')])
    amc_customer = fields.Boolean(string="Amc Customer", related='pending_enquiry.amc_customer')
    customer_name = fields.Many2one('res.partner', string="Customer Name", required=1,
                                    domain=[("customer_rank", ">", 0)])
    quote_date = fields.Date(string="Quotation Date", default=fields.Datetime.now)
    validity_date = fields.Integer(string="Validity")
    name = fields.Char(string="Quotation Number", copy=False)
    # address
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()

    machine_id = fields.Many2one('product.product', string="Machine", domain=[('is_machine', '=', True)], )
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
    service_required = fields.Char(string="Service Required")
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'),
                              ('submit', 'Submitted'), ('approved', 'Approved'),
                              ('rejected', 'Rejected'), ('done', 'Done')],
                             default='draft', readonly=True, string='States')
    work_order_count = fields.Integer(compute='_compute_order_count')
    price = fields.Float(string="Price", required=1)
    signed_name = fields.Char(string="Name")
    telephone = fields.Char(string="Telephone")
    scope_of_work = fields.Many2one('workshop.scopeofwork', string="Scope of Work")
    scope_of_work_description = fields.Text(related='scope_of_work.description', string="Description")
    digital_signature = fields.Binary(string='Signature')
    work_quotation_line_ids = fields.One2many('work.quotation.line', 'quotation_id')
    parts_required = fields.One2many('quotation.required.parts', 'quotation_part_link',
                                     string="Parts Required")
    services = fields.One2many('quotation.services', 'service_quotation', string="Services")
    other_cost_information = fields.One2many('other.quotation.charges', 'work_quotation_id')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    company_street = fields.Char(related='company_id.street')
    company_street2 = fields.Char(related='company_id.street2')
    company_city = fields.Char(related='company_id.city')
    company_zip = fields.Char(related='company_id.zip')
    company_state = fields.Many2one('res.country.state', related='company_id.state_id')
    company_country = fields.Many2one('res.country', related='company_id.country_id')
    quote_address_person = fields.Char(string='Quotation Addressing Person')
    amount_total = fields.Float(string='Amount Total', compute='_compute_amount')
    amount_untaxed = fields.Float(string='Amount Untaxed', compute='_compute_amount')
    amount_tax = fields.Float(string='Amount Tax', compute='_compute_amount')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    def _compute_amount(self):
        for quotation in self:
            quotation.amount_total = sum(quotation.work_quotation_line_ids.mapped('price_total'))
            quotation.amount_untaxed = sum(quotation.work_quotation_line_ids.mapped('price_subtotal'))
            quotation.amount_tax = sum(quotation.work_quotation_line_ids.mapped('price_tax'))

    def _get_default_currency_id(self):
        """gets company currency"""
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id)
    comments = fields.Text(string='Additional Notes')

    @api.constrains('price')
    def _check_price(self):
        # additional condition self.pending_enquiry for independent quotation creation odox
        if self.pending_enquiry:
            if self.price == 0:
                raise UserError(_("Price cannot be set as zero"))



    @api.onchange('machine_id')
    def _onchange_machine_id(self):
        if self.machine_id:
            machine = self.env['product.template'].search([('id', '=', self.machine_id.product_tmpl_id.id)])
            # product_varient = self.env['product.product'].search([('product_tmpl_id', '=', product_template.id)])
            print("!!!!!!!!",machine)
            self.made = machine.made
            self.make = machine.make
            self.kilo = machine.kilo
            self.kva = machine.kva
            self.horsepower = machine.horsepower
            self.machine_serial_number = machine.machine_serial_number
            self.item_code = machine.item_code
            self.rpm = machine.rpm
            self.pole = machine.pole
            self.volt = machine.volt
            self.amps = machine.amps
            self.hertz = machine.hertz
            self.motor_no = machine.motor_no

    def _compute_order_count(self):
        """count of work orders created for this quotation"""
        self.work_order_count = self.env['workshop.order'].search_count(
            [('pending_enquiry', '=', self.id)]) or 0

    def validate(self):
        """Adds sequence code to each record while creating it"""
        self.state = 'submit'
        sequence = self.env['ir.sequence']
        self.name = sequence.next_by_code('workshop.quotation.code') or _('New')

    @api.model
    def create(self, vals):
        """Sets sequence code to '/'"""
        vals['name'] = '/'
        return super(WorkshopQuotation, self).create(vals)

    def unlink(self):
        """restricts deletion of record once number is generated"""
        for move in self:
            if move.name != '/' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been validated once."))
        return super(WorkshopQuotation, self).unlink()

    def workorder(self):
        """creates work order"""

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
            'customer_name': self.customer_name.id,
            'pending_enquiry': self.id,
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
            }) for lines in self.pending_enquiry.parts_required]})

        work_order.customer_name = self.pending_enquiry.customer_name
        work_order.order_priority = self.pending_enquiry.service_priority
        work_order.initial_inspection = self.pending_enquiry.id
        self.state = 'done'
        return {
            'name': 'Work Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'workshop.order',
            'res_id': work_order.id,
            'target': 'current'
        }

    def approve(self):
        """approve quote"""
        self.state = 'approved'
        self.pending_enquiry.state = 'done'

    def reject(self):
        """rejects quote"""
        self.state = 'rejected'

    def set_to_draft(self):
        """rejects quote"""
        self.state = 'draft'

    @api.onchange('pending_enquiry')
    def onchange_pending_enquiry(self):
        """fills machine data"""
        data = ['kilo', 'kva', 'horsepower', 'machine_serial_number', 'item_code', 'rpm', 'made', 'make', 'pole',
                'volt',
                'amps', 'hertz', 'motor_no']
        if self.pending_enquiry.machine_type:
            machine_details = self.pending_enquiry.machine_type.read(data)[0]
            machine_details.pop('id')
            machine_details['machine_id'] = self.pending_enquiry.machine_type.id
            machine_details['customer_name'] = self.pending_enquiry.customer_name.id

            self.update(machine_details)
            self.price = self.pending_enquiry.work_price
            self.add_address()

    @api.onchange('customer_name')
    def add_address(self):
        """fills customer data"""
        if self.customer_name:
            data = ['street', 'street2', 'city', 'state_id', 'zip', 'country_id']
            values = self.customer_name.read(data)[0]
            values.pop('id')
            self.update(values)

    def button_work_order(self):
        """views linked work orders"""
        return {
            'name': 'Work Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'workshop.order',
            'domain': [('pending_enquiry', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    def button_sale_order(self):
        """views linked Sale orders"""
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('work_quotation_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    def send_by_mail(self):
        """send by email"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('workshop.email_template_quotation')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'workshop.quotation',
            'default_res_id': self.id,
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

    def generate_sale_order(self):
        so_vals = {
            'partner_id': self.customer_name.id,
            'company_id': self.company_id.id,
            'partner_invoice_id': self.customer_name.id,
            'partner_shipping_id': self.customer_name.id,
            'is_w_sale': True,
            'work_quotation_id': self.id,
            'order_line': [(0, 0, {
                'name': lines.name,
                'display_type': lines.display_type,
                'product_id': lines.product_id.id,
                'product_uom_qty': lines.product_uom_qty,
                'product_uom': lines.product_uom.id,
                'price_unit': lines.price_unit,
                'tax_id': lines.tax_id.ids,
            }) for lines in self.work_quotation_line_ids],
        }
        sale_order_id = self.env['sale.order'].create(so_vals)
        self.sale_order_id = sale_order_id.id


class WorkQuotationLine(models.Model):
    _name = 'work.quotation.line'

    quotation_id = fields.Many2one('workshop.quotation')
    product_id = fields.Many2one('product.product', string='Machine Details')
    name = fields.Char(string='Type Of Services')
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], default=False, help="Technical field for UX purpose.")
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', readonly=True, store=True)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the Quotation line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.quotation_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.quotation_id.customer_name)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


class QuotationPartsRequired(models.Model):
    _name = 'quotation.required.parts'
    _description = 'Quotation Required Parts'

    product_id = fields.Many2one('product.product', domain=[('type', '=', 'product')], string="Product")
    quantity = fields.Float(string="Quantity", default=1)
    product_unit = fields.Many2one('uom.uom', string="Unit")
    quotation_part_link = fields.Many2one('workshop.quotation', string="Quotation", copy=False)
    order_parts = fields.Many2one('workshop.order', string="Order Parts", copy=False)
    is_available = fields.Boolean(string="Is Available")
    m_parts_link = fields.Many2one('product.product', string="Order", copy=False)
    contract_parts = fields.Many2one('workshop.contract', string="Contract")
    cost = fields.Float(string="Cost")
    contract_sale_product = fields.Many2one('product.product', string="Machine")


class QuotationServices(models.Model):
    _name = 'quotation.services'
    _description = 'Quotation Services'

    total_hours = fields.Float(string="Total hrs for completion", default=1.0)
    mechanical_works = fields.Many2one('product.product', domain=[('type', '=', 'service'), ('is_machine', '=', False),
                                                                  ('is_workshop_service', '=', True)],
                                       string="Mechanical Works/Service List")
    cost = fields.Float(string="Cost")
    service_quotation = fields.Many2one('workshop.quotation', string="Work Quotation")
    machine = fields.Many2one('product.product')
    contract_machine = fields.Many2one('workshop.contract', string="Contract")
    contract_sale_product = fields.Many2one('product.product', string="Machine")


class OtherQuotationCharges(models.Model):
    _name = 'other.quotation.charges'
    _description = 'Other Quotation Charges'

    work_quotation_id = fields.Many2one('workshop.quotation')
    charge_description = fields.Char(string='Description')
    charge_cost = fields.Float(string='Cost')
