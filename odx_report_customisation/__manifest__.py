# -*- coding: utf-8 -*-
{
    'name': 'Report Customisation',
    'version': '15.0.1.1.0',
    'category': 'Customisation',
    'summary': """""",
    'category': 'Extra Tools',
    'author': 'Odox Softhub',
    "license": "OPL-1",
    'website': 'https://www.odoxsofthub.com',
    'depends': ['sale','workshop','purchase_discount', 'purchase',],
    'data': [
        'report/report.xml',
        'report/quotation_report_template.xml',
        'report/invoice_template.xml',
        'report/delivery_note_template.xml',
        'report/layout.xml',
        'report/purchase_order_template.xml',
        'views/purchase_order.xml',
        'views/delivery_note.xml',
        'views/workshop_quotation_view.xml',
        'views/res_users_view.xml',
        'views/account_move.xml',

    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,

}
