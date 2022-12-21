from odoo import api, fields, models


class InvoiceRelation(models.Model):
    _inherit = 'account.move'

    odx_machine_name = fields.Char(string="Machine Name", compute="compute_machine_name")
    odx_motor_rating = fields.Char(string="Machine Rating", compute="compute_machine_type")
    odx_serial_number = fields.Char(string="Serial Number",)  # imp
    odx_serial = fields.Char(compute='compute_serial')        #imp
    odx_gate_pass = fields.Char(string="Gate Pass No ")
    odx_authorized_signature = fields.Binary(string='Signature')
    odx_header = fields.Boolean(string="Print Header")
    odx_asset_number = fields.Char(string="Asset Number")



    def compute_machine_name(self):
        # print(self.invoice_line_ids[0].name, 'iuhiu')
        txt = self.invoice_line_ids[0].name
        x = txt.split(", ")
        firstElement = x[0]
        self.odx_machine_name = firstElement

    def compute_machine_type(self):
        lst = []
        txt = self.invoice_line_ids[0].name
        x = txt.split(", ")
        firstElement = x[2]
        lst.append(firstElement)
        secondElement = x[1]
        lst.append(secondElement)
        thirdElement = x[3]
        lst.append(thirdElement)
        motor_rating = ','.join(lst)
        self.odx_motor_rating = motor_rating


    def compute_serial(self):
        serail = self.env['product.template'].search(
            [('name', '=', self.odx_machine_name)])
        print(serail)
        test = self.create({
            'odx_serial_number': serail.machine_serial_number})
        print(test.odx_serial_number, "@@@@@@@@@@@@@@@@@2")
        self.odx_serial=test.odx_serial_number







    #     txt = [rec.name][0]
    #     # print(type(txt))
    #     x = txt.split(", ")
    #     # print(x)
    #     firstElement = x[0]
    #     print(firstElement)
