# -*- coding: utf-8 -*-
{
    'name': "Timesheet - Payroll",
    'version': "13.0.0.1.0",
    'summary': """Payroll Computed based on Timesheets of Employees.""",
    'description': """Payroll Computed based on Timesheets of Employees.""",
    'author': "Cybrosys Techno Solutions",
    'company': "Cybrosys Techno Solutions",
    'website': "https://cybrosys.com/",
    'category': "Generic Modules/Human Resources",
    'depends': ['hr_payroll', 'hr_contract', 'hr_timesheet', 'sale_management'],
    'data': [
        'data/data.xml',
        'data/paper_format.xml',
        'views/timesheet_costs.xml',
        'views/project_task_view_inherited.xml',
    ],
    'demo': [],
    'license': "LGPL-3",
    'installable': True,
    'application': True
}
