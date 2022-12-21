# -*- coding: utf-8 -*-
##############################################################################
# Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
# Author  : Cybrosys Techno Solutions (odoo@cybrosys.com)
# Licence : GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3)
##############################################################################

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    mechanical_work_order_id = fields.Many2one('mechanical.work.order', string="Mechanical Work Order",
                                               ondelete="restrict")
