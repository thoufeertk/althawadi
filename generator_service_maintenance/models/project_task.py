# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTasks(models.Model):
    _inherit = 'project.task'

    generator_service = fields.Many2one('generator.service', string="Service")


# class AccountAnalyticLine(models.Model):
#     _inherit = 'account.analytic.line'
    #
    # @api.onchange('employee_id')
    # def onchange_generator_employee_id(self):
    #     """This returns a domain that restrict the employees which not take part in the
    #     work order to add the timesheets"""
    #     res = {'domain': {'employee_id': [
    #         ('id', 'in', self.task_id.generator_service.service_technician.ids)]}}
    #     return res
