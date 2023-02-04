{
    'name': 'Workshop Management',
    'summary': """This module will manage Workshop, need to add compute function to total""",
    'version': '13.0.3.3.2',
    'description': """This module will manage Workshop""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://cybrosys.com',
    'category': 'Tools',
    'depends': ['account_accountant', 'stock', 'project_data', 'cy_timesheet_payroll', 'purchase', 'sale',
                'electrical_services', 'account_invoice_format', 'mail'],
    'license': 'AGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'report/report_contract_template.xml',
        'report/delivery_note_report.xml',
        'report/report_enquiry.xml',
        'report/report_initial_diagnosis.xml',
        'report/report_work_order.xml',
        'report/report_contract.xml',
        'report/report.xml',
        'data/workshop_mail.xml',
        'data/data.xml',
        'views/enquiry_register.xml',
        'views/machine_type.xml',
        'views/res_partner_inherited.xml',
        'views/workshop_config.xml',
        'views/machine_product_view.xml',
        'views/product_product_inherited.xml',
        'views/contract.xml',
        'views/initial_inspection.xml',
        'views/sale_order_view.xml',
        'views/mechanical_report.xml',
        'views/worshop_quotation.xml',
        'views/work_order.xml',
        'views/material_request.xml',
        'views/delivery_note.xml',
        'views/account_invoice.xml',
        'views/timesheet.xml',
        'views/product.xml',
        'views/workshope_scopeofwork_view.xml',
        'views/workshop_details_view.xml',
        'views/workshop_testing_inspection_view.xml',
        'views/workshop_extend_of_quotes_view.xml',
        'views/workshop_delivery.xml',
        'views/workshop_payment_terms.xml',
        'views/workshop_warranty_view.xml',
        'wizard/workshop_report.xml',
        'report/report_workshop_template.xml',
        'report/report_mechanical_template.xml',
        'report/report_quotation_template.xml',
        'report/material_request_report.xml',
        'wizard/contract_report.xml',
        'wizard/purchase_order_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
