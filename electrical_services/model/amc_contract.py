# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AnnualContract(models.Model):
    _name = 'amc.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    _description = "AMC Contract"

    def _get_default_currency_id(self):
        """gets company currency"""
        return self.env.user.company_id.currency_id.id

    name = fields.Char(default='New')
    amc_customer_id = fields.Many2one('res.partner', string='Customer Name',
                                      required=True)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=_get_default_currency_id)
    amc_start_date = fields.Date(string='Start date',
                                 default=fields.Date.today(), required=True)
    amc_end_date = fields.Date(string='End date', required=True)
    amc_contract_amount = fields.Float(string='Price', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('running', 'Running'),
        ('reject', 'Rejected'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', copy=False)
    amc_electrical_scope_ids = fields.One2many(
        'amc.electrical.scope.line', 'amc_contract_id')
    amc_electrical_parts_ids = fields.One2many('amc.electrical.parts.line',
                                               'amc_contract_parts_id')
    invoice_count = fields.Integer("Invoice Count", compute="_invoice_count")
    sale_order_reference = fields.Many2one('sale.order')

    def unlink(self):
        for contract in self:
            if contract.state == 'running':
                raise UserError(_("You cannot delete a contract in the running state"))
        return super(AnnualContract, self).unlink()

    def action_submit(self):
        """This is the submit function of the amc which changes the state of the record to
        submit"""
        running_contracts = self.env['amc.contract'].search(
            [('amc_customer_id', '=', self.amc_customer_id.id),
             ('state', '=', 'running')])
        if running_contracts:
            raise ValidationError(
                "You cannot have more than one running contracts for a customer!!!")
        self.sudo().write({
            'state': 'submit'
        })
        self.name = self.env['ir.sequence'].next_by_code('amc.contract')

    def action_approve(self):
        """This is the approve function which changes the state to running"""
        self.sudo().write({
            'state': 'running'
        })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Annual Contract Is Approved',
                'type': 'rainbow_man',
            }
        }

    def action_reject(self):
        """This is the reject function which send the corresponding record to the
        rejected list"""
        self.sudo().write({
            'state': 'reject'
        })

    @api.onchange('amc_electrical_scope_ids')
    @api.depends('amc_electrical_scope_ids')
    def _onchange_amc_electrical_scope_ids(self):
        """ Get values from electrical spare parts and assign to Bill of material in AMC contract"""
        spare_parts_list = [(5, 0, 0)]
        for spare_parts_ids in self.amc_electrical_scope_ids:
            if spare_parts_ids:
                for spares in spare_parts_ids.amc_scope_id.electrical_spare_parts_ids:
                    spare_parts_vals = {
                        'amc_parts_id': spares.spare_product_id.id,
                        'amc_parts_qty': spares.spare_product_quantity,
                        'amc_parts_unit_price': spares.spare_product_price,
                    }
                    spare_parts_list.append((0, 0, spare_parts_vals))
        self.update({'amc_electrical_parts_ids': spare_parts_list})

    def _invoice_count(self):
        query = """ SELECT am.id FROM account_move am
                            JOIN electrical_work_order ewo
                            ON ewo.id = am.electrical_work_order_id
                            JOIN electrical_enquiry_register eer
                            ON eer.id = ewo.enquiry_id
                            WHERE eer.contract_id = '%s' """ % (
            self.id)
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        self.invoice_count = len(res)

    def button_invoices(self):
        """Button to show invoices related invoices"""

        query = """ SELECT am.id FROM account_move am
                    JOIN electrical_work_order ewo
                    ON ewo.id = am.electrical_work_order_id
                    JOIN electrical_enquiry_register eer
                    ON eer.id = ewo.enquiry_id
                    WHERE eer.contract_id = '%s' """ % (
            self.id)
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        result['domain'] = [('id', 'in', res[0])]
        return result

    @api.onchange('sale_order_reference')
    def _onchange_sale_order_reference(self):
        self.amc_customer_id = self.sale_order_reference.partner_id.id
        scope_list = [(5, 0, 0)]
        for order_line in self.sale_order_reference.order_line:
            vals = {
                'amc_scope_id': order_line.product_id.id,
                'amc_scope_code': order_line.product_id.default_code,
                'amc_scope_description': order_line.product_id.electrical_item_description,
                'amc_scope_price': order_line.price_unit,
            }
            scope_list.append((0, 0, vals))
            self.update({'amc_electrical_scope_ids': scope_list})


class ElectricalScopeLine(models.Model):
    _name = 'amc.electrical.scope.line'
    _description = 'Contract Electrical Scope'

    amc_scope_id = fields.Many2one('product.product', string='Electrical Scope',
                                   domain=[('is_electrical', '=', True)])
    amc_scope_code = fields.Char(string='Item code',
                                 related='amc_scope_id.default_code')
    amc_scope_description = fields.Char(string='Item description',
                                        related='amc_scope_id.electrical_item_description')
    amc_scope_price = fields.Float(string='Amount')
    amc_contract_id = fields.Many2one('amc.contract')

    @api.onchange('amc_scope_id')
    def _onchange_amc_scope_id(self):
        self.amc_scope_price = self.amc_scope_id.lst_price


class ElectricalPartsLine(models.Model):
    _name = 'amc.electrical.parts.line'
    _description = 'Contract Electrical Spare Parts'

    amc_contract_parts_id = fields.Many2one('amc.contract')
    amc_parts_id = fields.Many2one('product.product', string='Product')
    amc_parts_qty = fields.Char(string='Quantity', default=1.0)
    amc_parts_unit_price = fields.Float(string='Unit Price')
