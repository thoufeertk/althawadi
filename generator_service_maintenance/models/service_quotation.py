# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ServiceQuotation(models.Model):
    _name = "service.quotation"
    _rec_name = 'name'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Service Quotation'

    service_date = fields.Datetime(string='Service Date', required=True)
    service_customer = fields.Many2one('res.partner', string='Customer')
    service_type = fields.Selection([('monitor', 'Monitor Service'),
                                     ('deployment', 'Deployment Service'),
                                     ('breakdown', 'Breakdown Service'),
                                     ('routine', 'Routine Maintenance'),
                                     ], string='Service Type', default='monitor', track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    reference = fields.Many2one('generator.service', string='Reference')
    service_estimated_cost = fields.Float(string='Estimated Service Cost')
    service_generator_id = fields.Many2one('product.product', string='Generator')
    service_engine_fsd_number = fields.Char(string='Engine FSD Number', required=True, store=True)
    service_generator_name = fields.Char(string='Generator Name', readonly=True)
    service_generator_image = fields.Binary()
    service_generator_serial_number = fields.Char(string='Generator Serial No', readonly=True)
    service_generator_kva_ph = fields.Char(string='Generator KVA/PH', readonly=True)
    service_engine_serial_number = fields.Char(string='Engine Serial No', readonly=True)
    service_engine_model = fields.Char(string='Engine Model', readonly=True)
    service_alternator_serial_number = fields.Char(string='Alternator Serial Number', readonly=True)
    service_alternator_frame_size = fields.Char(string='Alternator Frame Size', readonly=True)
    service_panel_amf = fields.Char(string='Panel - AMF/Manual (PIU)', readonly=True)
    service_panel_amf_make = fields.Char(string='AMF Panel / PIU Make', readonly=True)
    service_last_hours = fields.Char(string='Last Serv.Hours & Date', readonly=True)
    service_road_number = fields.Char(string='Road Number')
    service_bld_number = fields.Char(string='Bld No./Sub Station No')
    service_area_number = fields.Char(string='Area Number')
    service_area = fields.Char(string='Area')
    service_generator_running_hours = fields.Float(string='Running Hours')
    service_generator_piu_running_hours = fields.Float(string='PIU Running Hrs')
    service_breakdown_date = fields.Date(string='Breakdown Date')
    service_initial_fault = fields.Char(string='Initial Fault Found')
    service_rectifications = fields.Char(string='Rectifications')
    service_generator_spare_parts_ids = fields.One2many('service.quotation.spare.line', 'service_spare_parts_id')
    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'rejected')],
                             string="Status", readonly=True, default='draft', copy=False)
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
    scope_of_work = fields.Text(string="Scope Of Work")

    @api.model
    def create(self, vals):
        """Here the create function is override for the creation of the sequence
        of the service quotation"""
        vals['name'] = self.env['ir.sequence'].next_by_code('service.quotation')
        return super(ServiceQuotation, self).create(vals)

    def unlink(self):
        for move in self:
            if move.state != 'draft':
                raise UserError(_("You cannot delete an entry which has been validated once."))
        return super(ServiceQuotation, self).unlink()

    def quotation_approve(self):
        """This is the approve function of the quotation and in this function changes the
        state of the corresponding service to draft and state of quotation to approve"""
        service_id = self.env['generator.service'].search(
            [('id', '=', self.reference.id)])
        service_id.sudo().write({
            'state': 'draft'
        })
        self.sudo().write({
            'state': 'approve'
        })

    def quotation_reject(self):
        """This is the reject function of the quotation and it holds the state of
        corresponding service to waiting and of quotation to rejected"""
        service_id = self.env['generator.service'].search(
            [('id', '=', self.reference.id)])
        service_id.sudo().write({
            'state': 'waiting'
        })
        self.sudo().write({
            'state': 'reject'
        })

    @api.onchange('reference')
    def _onchange_reference(self):
        """In this onchange function loads the required details of the service to
        the corresponding quotation"""
        if self.reference:
            service_details = self.reference.read(['service_generator_id',
                                                   'service_customer',
                                                   'service_estimated_cost',
                                                   'service_engine_fsd_number',
                                                   'service_generator_kva_ph',
                                                   'service_engine_serial_number',
                                                   'service_engine_model',
                                                   'service_alternator_serial_number',
                                                   'service_alternator_frame_size',
                                                   'service_panel_amf',
                                                   'service_panel_amf_make',
                                                   'service_last_hours',
                                                   'service_generator_spare_parts_ids',
                                                   'service_area_number',
                                                   'service_bld_number',
                                                   'service_road_number',
                                                   'service_area',
                                                   'service_generator_running_hours',
                                                   'service_generator_piu_running_hours'])[0]
            service_details.pop('id')
            self.update(service_details)


class ServicesQuotationGeneratorSpareLine(models.Model):
    _name = "service.quotation.spare.line"
    _description = 'Service quotation spare line'

    service_spare_parts_id = fields.Many2one('service.quotation')
    service_generator_spare_parts = fields.Many2one('product.product', string="Spares")
    service_generator_spare_parts_cost = fields.Float(string="Unit Price")
    service_generator_spare_parts_qty = fields.Float(string="Quantity", default=1.0)
    generator_spare_parts_uom = fields.Many2one('uom.uom', string='Unit')
