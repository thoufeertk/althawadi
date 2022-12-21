# -*- coding: utf-8 -*-
{
    'name': 'New Generator Sales',
    'version': '13.0.4.0.1',
    'category': 'Sales',
    'summary': """This module is used for the new generator sales""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['generator_service_maintenance', 'sale_management'],
    'data': [
        'views/sale_order_inherited.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
