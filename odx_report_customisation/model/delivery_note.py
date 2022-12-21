from odoo import api, fields, models


class InvoiceRelation(models.Model):
    _inherit = 'delivery.note'


    odx_motor_rating = fields.Char(string="Machine Rating", compute="compute_machine_rating")

    odx_gate_pass_no = fields.Char(string="Gate Pass No")
    odx_delivered_by = fields.Char(string="Delivered By")
    odx_driver = fields.Char(string="Driver")
    odx_vehicle_no = fields.Char(string="Vehicle No.")
    odx_received_by = fields.Char(string="Received By")
    odx_receiver_phone = fields.Char(string="Phone")
    odx_location = fields.Char(string="Location")
    odx_received_date = fields.Date(string="Received Date")
    odx_header = fields.Boolean(string="Print Header")
    odx_asset_no = fields.Char(string="Asset Number")
    odx_date_of_supply =fields.Date(string="Date of Supply")

    def compute_machine_rating(self):
        lst = []
        txt = self.delivery_note_line[0].name
        x = txt.split(", ")
        firstElement = x[2]
        lst.append(firstElement)
        secondElement = x[1]
        lst.append(secondElement)
        thirdElement = x[3]
        lst.append(thirdElement)
        motor_rating = ','.join(lst)
        self.odx_motor_rating = motor_rating