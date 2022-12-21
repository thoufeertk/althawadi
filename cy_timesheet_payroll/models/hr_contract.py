# -*- coding: utf-8 -*-
from odoo import models, fields, _


class HrContractExt(models.Model):
    _inherit = 'hr.contract'
    _description = 'HR Contract'

    normal_overtime_wage = fields.Monetary('Normal OT Wage',  tracking=True,
                                           help="Employee's monthly overtime holiday wage.")
    holiday_overtime_wage = fields.Monetary('Holiday OT Wage',  tracking=True,
                                            help="Employee's monthly overtime holiday wage.")
