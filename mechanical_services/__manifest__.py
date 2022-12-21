# -*- coding: utf-8 -*-
{
    'name': 'Mechanical Services',
    'version': '13.0.1.0.0',
    'category': 'Maintenance',
    'summary': """This module includes work flow of mechanical works.
    based on the annual maintenance contract""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['stock', 'account_accountant', 'purchase', 'project_data', 'hr_timesheet',
                'cy_timesheet_payroll', 'sale_management', 'electrical_services','account_invoice_format','mail','contacts','sale'],
    'data': [
        'data/mechanical_sequence.xml',
        'data/groups.xml',
        'data/mechanical_journal.xml',

        'report/mechanical_reports.xml',
        'data/email_template.xml',

        'security/ir.model.access.csv',
        'views/mechanical_scope_view.xml',
        'views/product_product_inherited.xml',
        'views/product_template_inherited.xml',
        'views/mech_amc_contract_view.xml',
        'views/mechanical_enquiry_register_view.xml',
        'views/mechanical_quotation_view.xml',
        'views/mechanical_work_order_view.xml',
        'views/sale_order_inherited.xml',
        'views/project_task_inherited.xml',
        'views/mech_material_request_view.xml',
        # 'views/res_config_settings.xml',
        'report/mech_monthly_report_template.xml',
        'wizard/mechanical_report_wizard_view.xml',
        'report/mechanical_report_quotation.xml',
        'report/mech_material_request.xml',
        'views/mech_completion_certificate.xml',
        'report/mech_completion_certificate.xml',
        'wizard/mech_certificate_view.xml',
        'wizard/mech_po_wizard_view.xml',
        'report/mech_certificate_template.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,

}
