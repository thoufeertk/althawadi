# -*- coding: utf-8 -*-
##############################################################################
# Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
# Author  : Cybrosys Techno Solutions (odoo@cybrosys.com)
# Licence : GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3)
##############################################################################

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    electrical_work_order_id = fields.Many2one('electrical.work.order', string="Electrical Work Order",
                                               ondelete="restrict")

    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #     sale_order_id = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
    #
    #     return res
