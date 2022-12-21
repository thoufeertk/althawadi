from odoo import api, fields, models, _


class PartsRequired(models.Model):
    _name = 'required.parts'
    _description = 'Required Parts'

    product_id = fields.Many2one('product.product', domain=[('type', '=', 'product')], string="Product")
    quantity = fields.Float(string="Quantity", default=1)
    product_unit = fields.Many2one('uom.uom', string="Unit")
    inspection_part_link = fields.Many2one('initial.inspection', string="Inspection", copy=False)
    order_parts = fields.Many2one('workshop.order', string="Order Parts", copy=False)
    is_available = fields.Boolean(string="Is Available")
    m_parts_link = fields.Many2one('product.template', string="Order", copy=False)
    contract_parts = fields.Many2one('workshop.contract', string="Contract")
    cost = fields.Float(string="Cost")
    contract_sale_product = fields.Many2one('product.product', string="Machine")

    @api.onchange('product_id')
    def onchange_product_values(self):
        self.product_unit = self.product_id.uom_id
        self.cost = self.product_id.lst_price

    @api.onchange('quantity')
    def onchange_quantity(self):
        self.cost = self.product_id.lst_price * self.quantity


class ServicesRequired(models.Model):
    _name = 'workshop.services'
    _description = 'Workshop Services'

    total_hours = fields.Float(string="Total hrs for completion", default=1.0)
    mechanical_works = fields.Many2one('product.product', domain=[('type', '=', 'service'), ('is_machine', '=', False),
                                                                  ('is_workshop_service', '=', True)],
                                       string="Mechanical Works/Service List")
    cost = fields.Float(string="Cost")
    service_inspection = fields.Many2one('initial.inspection', string="Inspection")
    machine = fields.Many2one('product.template')
    contract_machine = fields.Many2one('workshop.contract', string="Contract")
    contract_sale_product = fields.Many2one('product.product', string="Machine")

    @api.onchange('mechanical_works', 'total_hours')
    def onchange_mechanical_works(self):
        self.cost = self.total_hours * self.mechanical_works.lst_price
