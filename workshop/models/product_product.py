# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_machine = fields.Boolean(string='Is Machine')
    is_workshop_service = fields.Boolean()
    category = fields.Many2one('machine.type', string="Machine Type/Category")
    machine_serial_number = fields.Char(string="Serial Number")
    made = fields.Char(string="Made")
    make = fields.Char(string="Make")
    kilo = fields.Char(string="Kilowatt (KW)")
    kva = fields.Char(string="KVA")
    horsepower = fields.Char(string="Horsepower")
    rpm = fields.Char(string="RPM")
    pole = fields.Char(string="Pole")
    volt = fields.Char(string="Volts")
    amps = fields.Char(string="Amps")
    hertz = fields.Char(string="Hertz")
    motor_no = fields.Char(string="Motor No.")
    service_required = fields.One2many('workshop.services', 'machine', string="Service Required")
    item_code = fields.Char(string="Item Code")
    # parts required
    m_parts_required = fields.One2many('required.parts', 'm_parts_link', string="Parts Required")
    product_template_value_ids = fields.One2many('product.template.attribute.value', 'attribute_line_id', string="Product Attribute Values")
    type = fields.Selection(
        selection=[
            ('consu', 'Consumable'),
            ('service', 'Service'),
            ('product','Storable Product')
        ],

        store=True,
        readonly=True,
    )




    @api.onchange('service_required')
    def _onchange_service_required(self):
        price_list = []
        for service in self.service_required:
            price_list.append(service.cost)
            print(price_list)
        print(sum(price_list))
        self.list_price = sum(price_list)


    def action_open_attribute_values(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Product Variant Values"),
            'res_model': 'product.template.attribute.value',
            'view_mode': 'tree,form',
            # 'domain': [('id', 'in', self.product_template_value_ids.ids)],
            'domain': [('product_tmpl_id', '=', self.id)],
            'views': [
                (self.env.ref('product.product_template_attribute_value_view_tree').id, 'list'),
                (self.env.ref('product.product_template_attribute_value_view_form').id, 'form'),
            ],
            'context': {
                'search_default_active': 1,
                'default_attribute_id':self.attribute_line_ids.attribute_id,
            },
        }

