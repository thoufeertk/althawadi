# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    electrical_order_id = fields.Many2one('electrical.work.order', string="Electrical Work Order")

    def submit_electrical_task(self):
        """Function for making the task completed.And allow to finish the
        electrical work order"""
        self.electrical_order_id.check_task_status = True
