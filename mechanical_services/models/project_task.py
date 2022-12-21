# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    mechanical_order_id = fields.Many2one('mechanical.work.order', string="Mechanical Work Order")

    def submit_mechanical_task(self):
        """Function for making the task completed.And allow to finish the
        mechanical work order"""
        self.mechanical_order_id.check_task_status = True
