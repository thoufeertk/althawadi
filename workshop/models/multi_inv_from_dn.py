from odoo import api, fields, models


class MultiInvoices(models.TransientModel):
    _name = 'delivery.invoices'
    _description = 'Invoicing Delivery Notes'

    def create_invoices_action(self):
        delivery_note_ids = self.env['delivery.note'].browse(self.env.context['delivery_note_ids'])
        target_ids = []
        for delivery_note in delivery_note_ids:
            for note_line in delivery_note.delivery_note_line:
                target_ids.append((0, 0, {
                    'name': note_line.description,
                    'quantity': note_line.qty,
                    'price_unit': note_line.rate,
                    'tax_ids': [(6, 0, note_line.tax.ids)],
                }))
        invoices = self.env['account.move'].create({
            'partner_id': delivery_note_ids.customer_name.id,
            'type': 'out_invoice',
            'pending_delivery_note': delivery_note_ids.ids,
            'invoice_line_ids': target_ids,
            'journal_id': int(self.env['ir.config_parameter'].sudo().get_param('workshop_journal_id')) or False
        })
        if self.env.context.get('view_invoice', False):
            return invoices.ids

    # def create_view_invoices_action(self):
    #     res = self.with_context({'view_invoice': True,
    #                              'delivery_note_ids': self.env.context['delivery_note_ids']
    #                              }).create_invoices_action()
    #     return {
    #         'name': 'Invoices',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move',
    #         'context': {
    #             'default_type': 'out_invoice',
    #             'journal_id': int(self.env['ir.config_parameter'].sudo().get_param('workshop_journal_id')) or False
    #         },
    #         'domain': [('id', 'in', res)],
    #         'target': 'current'
    #     }
