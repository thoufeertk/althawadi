from odoo import fields, models, api
from odoo.exceptions import UserError


class ServiceCompletion(models.Model):
    _name = 'service.completion'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Service Completion'

    name = fields.Char(string='name', compute='_compute_name')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    sale_order_ids = fields.One2many('sale.invoice.line', 'service_completion_id')
    state = fields.Selection([('draft', 'New'), ('invoiced', 'Invoiced')],
                             string="Status", readonly=True, default='draft')

    @api.depends('partner_id', 'start_date', 'end_date')
    def _compute_name(self):
        for completion in self:
            completion.name = str(completion.partner_id.name) + '-' + str(completion.start_date) + '->' + str(
                completion.end_date)

    def fetch_sale_data(self):
        """Function for fetching sales details within selected
        period and customer"""
        if self.partner_id and self.start_date and self.end_date:
            sale_order_ids = self.env['sale.order'].search(
                [('partner_id', '=', self.partner_id.id), ('date_order', '<=', self.end_date),
                 ('date_order', '>=', self.start_date)])
            sale_order_ids = sale_order_ids.filtered(lambda sale: sale.invoice_count == 0)
            sale_order_line = []
            self.sale_order_ids = [(5, 0, 0)]
            for sale_order in sale_order_ids:
                vals = (0, 0, {
                    'sale_order_id': sale_order.id,
                    'sale_amount': sale_order.amount_total,
                    'service_type': sale_order.gen_service_type,
                    'availability_reason': sale_order.availability_reason,
                    'allocated_no_service': sale_order.allocated_no_service,
                    'remaining_no_service': sale_order.remaining_no_service,
                })
                sale_order_line.append(vals)
            self.update({'sale_order_ids': sale_order_line})
        else:
            raise UserError("Fill Mandatory Details")

    def generate_invoice(self):
        """Generate invoices"""
        sale_order_ids = []
        for sale in self.sale_order_ids:
            sale_order_ids.append(sale.sale_order_id.id)
        sale_orders = self.env['sale.order'].browse(sale_order_ids)
        invoice = sale_orders._create_invoices()
        self.write({'state': 'invoiced'})
        invoice.update({'sale_order_ids': sale_order_ids})
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'context': {'create': False},
            'target': 'current'
        }


class SaleInvoiceLine(models.Model):
    _name = 'sale.invoice.line'
    _description = 'Sale Invoice Lines'

    service_completion_id = fields.Many2one('service.completion')
    sale_order_id = fields.Many2one('sale.order')
    sale_amount = fields.Float(string='Amount')
    service_type = fields.Selection([('monitor', 'Monitor Service'),
                                     ('deployment', 'Deployment Service'),
                                     ('breakdown', 'Breakdown Service'),
                                     ('routine', 'Routine Maintenance'),
                                     ], string='Service Type')
    allocated_no_service = fields.Integer(string='Allocated Service')
    remaining_no_service = fields.Integer(string='Remaining Service')
    availability_reason = fields.Char(string='Availability')
    invoice_eligibility = fields.Boolean(string='Invoice Eligibility', compute='_compute_invoice_eligibility')

    @api.depends('remaining_no_service')
    def _compute_invoice_eligibility(self):
        for line in self:
            if line.remaining_no_service != 0:
                line.invoice_eligibility = False
            else:
                line.invoice_eligibility = True
