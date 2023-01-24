"""Enquiry Register"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EnquiryRegister(models.Model):
    """Enquiry Register"""
    _name = 'enquiry.register'
    _rec_name = 'enquiry_number'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Enquiry Register"

    date_enquiry = fields.Date(string="Date", default=fields.Datetime.now)
    enquiry_number = fields.Char(string="Enquiry reference number", copy=False)
    customer_name = fields.Many2one('res.partner', string="Customer Name", required=1)
    service_priority = fields.Selection([('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
                                        default='high', string="Service Priority")
    service_deadline = fields.Date(string="Service deadline", required=1)
    repair_reason = fields.Text(string="Customer reason for repair")
    machine_type = fields.Many2one('product.product', string="Type of Machine",
                                   required=True, domain=[('is_machine', '=', True)])
    quantity = fields.Float(string="Quantity")
    # address
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'),
                              ('done', 'Done')], default='draft', readonly=True, string='States',
                             track_visibility='onchange')
    inspection_count = fields.Integer(compute='_compute_inspection_count')
    # warranty
    warranty_status = fields.Selection([
        ('with_warranty', 'Under Warranty'),
        ('no_warranty', 'No Warranty'),
    ], 'Warranty Status')

    def _compute_inspection_count(self):
        """Computes the no of inspections created for this enquiry"""
        for record in self:
            record.inspection_count = record.env['initial.inspection'].search_count(
                [('enquiry_number', '=', record.enquiry_number)]) or 0

    def validate(self):
        """Adds sequence code to each record while creating it"""
        self.state = 'pending'
        sequence = self.env['ir.sequence']
        self.enquiry_number = sequence.next_by_code('enquiry.register.code') or _('New')

    @api.model
    def create(self, vals):
        """Sets sequence code to /"""
        vals['enquiry_number'] = '/'
        return super(EnquiryRegister, self).create(vals)

    def unlink(self):
        """restricts deletion of record once number is generated"""
        for move in self:
            if move.enquiry_number != '/' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been validated once."))
        return super(EnquiryRegister, self).unlink()

    # @api.constrains('customer_name', 'service_deadline')
    # def check_customer_name(self):
    #     """Checks if running contract exists for this customer"""
    #     contract = self.env['workshop.contract']
    #     customer = self.customer_name.id
    #     deadline = self.service_deadline
    #     running_contract = contract.search(
    #         [('contract_partner_id', '=', customer), ('state', '=', 'running'),
    #          ('contract_start_date', '<=', deadline),
    #          ('contract_end_date', '>=', deadline)
    #          ])
    #     if running_contract:
    #         raise UserError("This customer already has a running contract on the given deadline")

    @api.onchange('customer_name')
    def add_address(self):
        """Adds customer data to the form"""
        customer = self.customer_name
        data = ['street', 'street2', 'city', 'state_id', 'zip', 'country_id']
        if customer:
            values = customer.read(data)[0]
            values.pop('id')
            self.update(values)

    def create_inspection(self):
        """creates inspection record with values from enquiry"""
        values = self.read(['enquiry_number', 'customer_name', 'service_priority',
                            'service_deadline', 'machine_type', 'quantity', 'repair_reason'])[0]
        values.pop('id')
        values['enquiry_number'] = self.id
        for data in values:
            if isinstance(values[data], tuple):
                values[data] = values[data][0]
        inspection_id = self.env['initial.inspection'].create(values)
        # inspection_id.machine_details()
        return {
            'name': 'Customers',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'initial.inspection',
            'res_id': inspection_id.id,
            'target': 'current'
        }

    def button_inspection(self):
        """returns view of inspections linked to the current enquiry"""
        return {
            'name': 'Inspection',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'initial.inspection',
            'domain': [('enquiry_number', '=', self.enquiry_number)],
            'context': {'create': False},
            'target': 'current'
        }
