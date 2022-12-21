# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    technician_ids = fields.Many2many('hr.employee')


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def default_get(self, field_list):
        result = super(AccountAnalyticLine, self).default_get(field_list)
        result['employee_id'] = ''
        return result

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        res = {'domain': {'employee_id': [
            ('id', 'in', self.task_id.technician_ids.ids)]}}
        return res
