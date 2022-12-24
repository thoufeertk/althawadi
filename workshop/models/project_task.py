from odoo import api, fields, models


class ProjectTaks(models.Model):
    _inherit = 'project.task'

    workshop_workorder = fields.Many2one('workshop.order', string="Workshop")


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    workshop_description = fields.Many2one('product.product',
                                           domain=[('type', '=', 'service'), ('is_machine', '!=', True)],
                                           string="Description ")

    @api.onchange('workshop_description')
    def onchange_workshop_description(self):
        self.name = self.workshop_description.name
        if self.task_id.workshop_workorder.initial_inspection:
            products = (
                self.task_id.workshop_workorder.initial_inspection.services.mapped('mechanical_works')).ids
            self.unit_amount = self.task_id.workshop_workorder.initial_inspection.services.filtered(
                lambda x: x.mechanical_works.id == self.workshop_description.id).total_hours
            return {'domain': {'workshop_description': [('id', 'in', products)]}}
