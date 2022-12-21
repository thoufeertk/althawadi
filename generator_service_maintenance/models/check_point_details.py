# -*- coding: utf-8 -*-

from odoo import models, fields


class ServiceQuotation(models.Model):
    _name = "check.point.details"
    _rec_name = 'name'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Check Point Description'

    name = fields.Char(string='Name', required=True)
