from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WorkshopContract(models.Model):
    _name = 'workshop.contract'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Contract"
    _rec_name = 'name'

    name = fields.Char(string="Number")
    contract_partner_id = fields.Many2one('res.partner', string="Customer Name",
                                          domain=[("customer_rank", ">", 0)],
                                          required=1)
    contract_start_date = fields.Date(string="Start Date", required=1)
    contract_end_date = fields.Date(string="End Date", required=1)
    original_amount = fields.Float(string="AMC Amount", required=1)
    contract_amount = fields.Float(string="AMC Balance", required=1)
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'),
                              ('running', 'Running'), ('reject', 'Rejected'),
                              ('expired', 'Expired')], default='draft',
                             readonly=True)
    invoice_count = fields.Integer('Invoices', compute="_invoice_count")
    machine = fields.Many2one('product.product', domain="[('is_machine','=',True)]")
    service_required = fields.One2many('workshop.services', 'contract_machine', string="Service Required")
    m_parts_required = fields.One2many('required.parts', 'contract_parts', string="Parts Required")
    sale_order = fields.Many2one('sale.order', string="Sale Order")
    machines = fields.Many2many('product.product', string="Machines")

    @api.onchange('sale_order')
    def sale_machines(self):
        self.machines = self.sale_order.order_line.mapped('product_id')
        self.contract_partner_id = self.sale_order.partner_id.id
        self.contract_amount = self.sale_order.amount_total
        self.original_amount = self.sale_order.amount_total

    @api.onchange('machines')
    def get_machine_data(self):
        self.m_parts_required = self.service_required = None
        if self.machines:
            query = """select product_id, quantity, m_parts_link as contract_sale_product, product_unit, cost 
            from required_parts where m_parts_link in %s"""
            self.env.cr.execute(query, [tuple(self.machines.ids)])
            parts = self.env.cr.dictfetchall()
            for part in parts:
                self.m_parts_required |= self.m_parts_required.new(part)
            query = """select mechanical_works, cost,machine as contract_sale_product, total_hours 
            from workshop_services where machine in %s"""
            self.env.cr.execute(query, [tuple(self.machines.ids)])
            services = self.env.cr.dictfetchall()
            for service in services:
                self.service_required |= self.service_required.new(service)

    @api.onchange('machine')
    def machine_details(self):
        """updates machine details"""
        self.m_parts_required = None
        self.service_required = None
        if self.machine:
            data = ['product_id', 'quantity', 'product_unit', 'cost']
            parts = self.machine.m_parts_required.read(data)
            for part in parts:
                for item in part:
                    if isinstance(part[item], tuple):
                        part[item] = part[item][0]
                part.pop('id')
                self.m_parts_required |= self.m_parts_required.new(part)
            data = ['mechanical_works', 'cost', 'total_hours']
            services = self.machine.service_required.read(data)
            for service in services:
                for item in service:
                    if isinstance(service[item], tuple):
                        service[item] = service[item][0]
                service.pop('id')
                self.service_required |= self.service_required.new(service)

    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=_get_default_currency_id)

    def unlink(self):
        """restricts deletion of record once validated"""
        for move in self:
            if move.state != 'draft':
                raise UserError(_("You cannot delete an entry which has been validated once."))
        return super(WorkshopContract, self).unlink()

    def _invoice_count(self):
        """Compute invoice count"""
        query = """ SELECT am.id FROM account_move am
                    JOIN account_move_delivery_note_rel amdnr
                    ON amdnr.account_move_id = am.id
                    JOIN delivery_note dn
                    ON dn.id = amdnr.delivery_note_id
                    JOIN workshop_order wo
                    ON wo.id = dn.job_reference
                    JOIN initial_inspection ii
                    ON ii.id = wo.initial_inspection
                    JOIN workshop_contract wc ON wc.id = ii.contract_id WHERE wc.id = '%s' """ % (
            self.id)
        self.env.cr.execute(query)
        res = [x[0] for x in self.env.cr.fetchall()]
        self.invoice_count = len(res)

    def button_invoices(self):
        query = """ SELECT am.id FROM account_move am
            JOIN account_move_delivery_note_rel amdnr
            ON amdnr.account_move_id = am.id
            JOIN delivery_note dn
            ON dn.id = amdnr.delivery_note_id
            JOIN workshop_order wo
            ON wo.id = dn.job_reference
            JOIN initial_inspection ii
            ON ii.id = wo.initial_inspection
            JOIN workshop_contract wc ON wc.id = ii.contract_id WHERE wc.id = '%s' """ % (
            self.id)
        self.env.cr.execute(query)
        res = [x[0] for x in self.env.cr.fetchall()]
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        result['domain'] = [('id', 'in', res)]
        return result

    @api.model
    def create(self, vals):
        if vals.get('enquiry_number', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'workshop.contract.code') or _('New')
        running_contract = self.env['workshop.contract'].search(
            [('contract_partner_id', '=', vals['contract_partner_id']),
             ('contract_end_date', '>=', self.contract_start_date),
             ('state', '=', 'running')])
        if running_contract:
            raise UserError("Running contract already exists")
        return super(WorkshopContract, self).create(vals)

    def action_submit(self):
        self.state = 'submit'

    def action_approve(self):
        self.state = 'running'

    def action_reject(self):
        self.state = 'reject'
