# -*- coding: utf-8 -*-
{
    'name': "td_sediagro_contratos",

    'summary': """
        Gestión de Contratos de Proveeduría""",

    'description': """
        Se crea un modelo nuevo para llevar un control de los contratos que realizan por ventas a largo plazo. 
    """,

    'author': "3Digital, S.A.",
    'website': "http://www.3digital.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','product'],

    # always loaded
    'data': [
        'security/sediagro_data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/ir_sequence_data.xml',
        'report/report_contrato.xml'
    ],
    'license': 'LGPL-3',
}