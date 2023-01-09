"""Workshop Order"""
from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class WorkshopOrder(models.Model):
    """Workshop Order"""
    _name = 'workshop.order'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Order"

    name = fields.Char(string="Order Number", copy=False)
    remove_check_button = fields.Boolean(string="Availability", default=False)
    customer_name = fields.Many2one('res.partner', string="Customer Name", required=True,
                                    domain=[("customer_rank", ">", 0)])
    pending_enquiry = fields.Many2one('workshop.quotation', string="Pending List",
                                      domain=[('state', '=', 'pending')])
    initial_inspection = fields.Many2one('initial.inspection', string="Initial Inspection",
                                         domain=[('state', '=', 'pending')])
    amc_customer = fields.Boolean(string="Amc Customer", related='initial_inspection.amc_customer')

    order_date = fields.Date(string="Date", default=fields.Datetime.now)
    workshop_picking_id = fields.Many2one('stock.picking', string='Related Picking')
    order_priority = fields.Selection([('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
                                      default='high', string="Service Priority")
    technician_ids = fields.One2many('workshop.order.technician', 'workshop_order_id')
    # Machine details
    category = fields.Many2one('machine.type', string="Machine Type/Category", related='initial_inspection.category')
    made = fields.Char(string="Made", related='initial_inspection.made')
    make = fields.Char(string="Make", related='initial_inspection.make')
    kilo = fields.Char(string="Kilowatt (KW)", related='initial_inspection.kilo')
    kva = fields.Char(string="KVA", related='initial_inspection.kva')
    horsepower = fields.Char(string="Horsepower", related='initial_inspection.horsepower')
    machine_serial_number = fields.Char(string="Serial Number", related='initial_inspection.machine_serial_number')
    item_code = fields.Char(string="Item Code", related='initial_inspection.item_code')
    rpm = fields.Char(string="RPM", related='initial_inspection.rpm')
    pole = fields.Char(string="Pole", related='initial_inspection.pole')
    volt = fields.Char(string="Volts", related='initial_inspection.volt')
    amps = fields.Char(string="Amps", related='initial_inspection.amps')
    hertz = fields.Char(string="Hertz", related='initial_inspection.hertz')
    motor_no = fields.Char(string="Motor No.", related='initial_inspection.motor_no')
    # Material Request details
    parts_required = fields.One2many('stock.move', 'workshop_order_move_id', string="Required Parts")
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('waiting_material', 'Waiting Material'),
                              ('running', 'Running'), ('submit', 'Submitted'),
                              ('approve', 'Approve'), ('reject', 'Reject'),
                              ('waiting', 'Waiting for Invoice'),
                              ('invoiced', 'Invoiced')],
                             default='draft', readonly=True)
    delivery_note_count = fields.Integer(compute='_compute_dn_count')
    material_request_count = fields.Integer(compute='_compute_dn_count', string='Material Request count',
                                            default=0)
    warranty_days = fields.Integer(string='Warranty Days')

    def _compute_dn_count(self):
        """count of delivery notes"""
        for rec in self:
            rec.delivery_note_count = self.env['delivery.note'].search_count(
                [('job_reference', '=', rec.id)]) or 0
            rec.material_request_count = self.env['workshop.material.request'].search_count(
                [('pending_list_id', '=', rec.id)]) or 0

    def validate(self):
        """Adds sequence code to each record while creating it"""
        self.state = 'pending'
        sequence = self.env['ir.sequence']
        self.name = sequence.next_by_code('workshop.order.code') or _('New')
        self.before_check_availability()

    @api.model
    def create(self, vals):
        """Sets sequence code to '/'"""
        vals['name'] = '/'
        return super(WorkshopOrder, self).create(vals)

    def unlink(self):
        """restricts deletion of record once number is generated"""
        for move in self:
            if move.name != '/' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been validated once."))
            if move.state == 'draft':
                if move.workshop_picking_id:
                    move.workshop_picking_id.unlink()
        return super(WorkshopOrder, self).unlink()

    @api.onchange('pending_enquiry')
    def onchange_pending_enquiry(self):
        """fills quote data"""
        if self.pending_enquiry:
            picking_type_id = self.env.ref('stock.picking_type_internal')
            location_id = picking_type_id.default_location_src_id.id
            destination_id = picking_type_id.default_location_dest_id.id
            if location_id and destination_id:
                picking_vals = {
                    'partner_id': self.customer_name.id,
                    'picking_type_id': picking_type_id.id,
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }
                picking_id = self.env['stock.picking'].sudo().create(picking_vals)
                self.workshop_picking_id = picking_id.id

            self.update({'parts_required': [(0, 0, {
                'picking_type_id': picking_type_id.id,
                'picking_id': picking_id.id,
                'name': lines.product_id.name,
                'product_id': lines.product_id.id,
                'product_uom': lines.product_id.uom_id.id,
                'product_uom_qty': lines.quantity,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': lines.product_id.workshop_stock_location.id,
            }) for lines in self.initial_inspection.parts_required]})
            self.customer_name = self.initial_inspection.customer_name
            self.order_priority = self.initial_inspection.service_priority
        else:
            self.parts_required = None

    def workshop_delivery_note(self):
        """creates delivery note"""
        self.pending_enquiry.state = 'done'
        delivery_line_ids = [(5, 0, 0)]
        for line in self.pending_enquiry.work_quotation_line_ids:
            sale_line = {
                'product_id': line.product_id.id,
                'name': line.name,
                'display_type': line.display_type,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
                'product_uom': line.product_uom.id,
                'discount': line.discount,
                'tax_id': line.tax_id.ids,
            }
            delivery_line_ids.append((0, 0, sale_line))
        delivery_note = self.env['delivery.note'].create({
            'job_reference': self.id,
            'purchase_date': self.order_date,
            'customer_name': self.customer_name.id,
            'sale_order': self.pending_enquiry.sale_order_id.id,
            'delivery_note_line': delivery_line_ids
        })
        return {
            'name': 'Delivery Note',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'delivery.note',
            'res_id': delivery_note.id,
            'target': 'current'
        }

    def button_delivery_note(self):
        """views linked delivery notes"""
        return {
            'name': 'Delivery Note',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'delivery.note',
            'domain': [('job_reference', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }

    def button_workshop_task(self):
        """views timesheet"""
        return {
            'name': 'Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('workshop_workorder', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }

    def before_check_availability(self):
        """This function checks availability of products"""
        moves = self.parts_required.filtered(
            lambda x: x.state not in ('done', 'cancel'))._action_confirm()
        moves._action_assign()
        MaterialRequest = self.env['workshop.material.request']
        MaterialRequestLine = self.env['work.material.request.bom.line']
        if any(line.state in ['confirmed', 'partially_available'] for line in self.parts_required):
            if self.material_request_count == 0:
                vals = {
                    'partner_id': self.customer_name.id,
                    'order_priority': self.order_priority,
                    'date': self.order_date,
                    'pending_list_id': self.id,
                }
                request_id = MaterialRequest.create(vals)
                MaterialRequestLine.create({
                                               'product_id': material_line.product_id.id,
                                               'quantity': material_line.product_uom_qty - material_line.reserved_availability,
                                               'material_request_id': request_id.id,
                                               'price': material_line.product_id.lst_price,
                                           } for material_line in
                                           self.parts_required.filtered(
                                               lambda line: line.state in ['confirmed', 'partially_available']))
        else:
            if self.workshop_picking_id:
                self.workshop_picking_id.origin = self.name
                for line in self.parts_required:
                    line.quantity_done = line.reserved_availability
                    line.workshop_order_move_id = self.id
                self.workshop_picking_id.button_validate()
                self.workshop_picking_id.message_post_with_view('mail.message_origin_link',
                                                                values={'self': self.workshop_picking_id,
                                                                        'origin': self},
                                                                subtype_id=self.env.ref('mail.mt_note').id)

    def work_start(self):
        technician_list = []
        for technician_line in self.technician_ids:
            technician_list.append(technician_line.technician_id.id)
        if not technician_list:
            raise ValidationError("Choose atleast one technician!!!")
        self.env['project.task'].create({
            'name': self.name,
            'kanban_state': 'normal',
            'project_id': self.env.ref('project_data.project_project_workshop').id,
            'partner_id': self.customer_name.id,
            'workshop_workorder': self.id,
            'priority': '1' if self.order_priority == 'high' else '0',
            'date_deadline': self.initial_inspection.service_deadline,
            'date_assign': date.today(),
            'technician_ids': technician_list,
        })
        self.sudo().write({
            'state': 'running'
        })

    def check_parts_availability(self):
        """
        Check the availability of Parts in stock.
        """
        moves = self.parts_required.filtered(
            lambda x: x.state not in ('done', 'cancel'))._action_confirm()
        moves._action_assign()
        if not any(line.state in ['confirmed', 'partially_available'] for line in self.parts_required):
            self.remove_check_button = True
        # else:
        #     self.state = 'pending'

    def work_submit(self):
        """submits order"""
        if any(line.state in ['confirmed', 'partially_available'] for line in self.parts_required):
            raise UserError("Parts are not available yet.")
        self.state = 'submit'

    def work_approve(self):
        """approves order"""
        self.state = 'approve'

    def work_reject(self):
        """rejects order"""
        self.state = 'reject'

    def action_view_material_request(self):
        """ View the related Material Request of the Service.
        """
        return {
            'name': _('Material Request'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'workshop.material.request',
            'domain': [('pending_list_id', '=', self.id)],
            'target': 'current',
            'context': {'create': False}
        }


class TechnicianDetails(models.Model):
    _name = 'workshop.order.technician'
    _description = 'Technician Details'

    workshop_order_id = fields.Many2one('workshop.order')
    technician_id = fields.Many2one('hr.employee', string='Name')
    job = fields.Selection([('technician', 'Technician'), ('winder', 'Winder'),
                            ('assembly', 'Assembly'), ('fitter', 'Fitter'),
                            ('testing', 'Testing')], string="Job", default='technician')
    # technician_phone = fields.Char(related='technician_id.work_phone', string='Phone')


class StockMove(models.Model):
    _inherit = 'stock.move'

    workshop_order_move_id = fields.Many2one('workshop.order', string="Workshop Order Reference")
