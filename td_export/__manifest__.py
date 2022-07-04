# -*- coding: utf-8 -*-
{
    'name': "td_export",

    'summary': """
        Agregar un botón para mostrar una vista de lista en los modelos""",

    'description': """
        Vista de lista para modelos
    """,

    'author': "3Digital",
    'website': "http://www.3digital.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'license': 'LGPL-3',
}