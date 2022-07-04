# -*- coding: utf-8 -*-
{
    'name': "account_aged_report",
    'license': 'LGPL-3',
    'summary': """
        Mejoras a Historial de pagos y cobros""",

    'description': """
        Agregando campos descriptivos a la tabla del listado de pagos y cobros.
    """,

    'author': "Soluciones Ágiles S. A.",
    'website': "www.inteligos.gt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Pagos y Cobros',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
}