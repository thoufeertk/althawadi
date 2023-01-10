"""Delivery note"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DeliveryNote(models.Model):
    """Delivery note"""
    _name = 'delivery.note'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _rec_name = 'delivery_note_no'
    _description = "Delivery Note"

    def _get_default_currency_id(self):
        """gets company currency"""
        return self.env.user.company_id.currency_id.id

    customer_name = fields.Many2one('res.partner', string="Customer name",
                                    domain=[("customer_rank", ">", 0)], required=1)
    show_price = fields.Boolean(string="Show Price in Report", related='customer_name.show_price_details')
    delivery_note_no = fields.Char(string="Delivery note number", copy=False)
    delivery_note_date = fields.Date(string="Delivery note date", default=fields.Datetime.now)
    purchase_date = fields.Date(string="Customer Purchase Order Date")
    job_reference = fields.Many2one('workshop.order', string="Our Job Reference",
                                    domain=[('state', '=', 'pending')], required=1)
    delivery_note_line = fields.One2many('delivery.note.line', 'delivery_note', string="Delivery Note Details")
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('invoiced', 'Invoiced')],
                             default='draft', readonly=True)
    sale_count = fields.Integer(compute='_compute_sale_count')
    sale_order = fields.Many2one('sale.order', string="Sale Order", domain=[('is_w_sale', '=', True)])
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id)

    def _compute_sale_count(self):
        """count of sale order linked"""
        self.sale_count = self.env['sale.order'].search_count(
            [('id', '=', self.sale_order.id)]) or 0

    def validate(self):
        """Adds sequence code to each record while creating it"""
        self.state = 'pending'
        self.job_reference.state = 'waiting'
        sequence = self.env['ir.sequence']
        if self.sale_order:
            self.sale_order.workshop_delivery_note = self.id
        self.delivery_note_no = sequence.next_by_code('delivery.note.code') or _('New')

    @api.model
    def create(self, vals):
        """Sets sequence code to '/'"""
        vals['delivery_note_no'] = '/'
        return super(DeliveryNote, self).create(vals)

    def unlink(self):
        """restricts deletion of record once number is generated"""
        for move in self:
            if move.delivery_note_no != '/' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been validated once."))
        return super(DeliveryNote, self).unlink()

    def button_sale(self):
        """views sale order"""
        sale_order = self.env['sale.order'].search([('id', '=', self.sale_order.id)])
        if sale_order:
            sale_order.workshop_delivery_note = self.id
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', '=', self.sale_order.id)],
            'context': {'create': False},
            'target': 'current'
        }

    @api.onchange('job_reference')
    def onchange_job_reference(self):
        """fills order data"""
        self.update({'purchase_date': self.job_reference.order_date,
                     'customer_name': self.job_reference.customer_name.id,
                     })
