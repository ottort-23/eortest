# -*- coding: utf-8 -*-
{
    'name': "td_sediagro",

    'summary': """
        Adecuacion Sediagro""",

    'description': """
        Adecuaciones para Sediagro
        Productos:
            - Composicion
    """,

    'author': "3Digital",
    'website': "http://www.3digital.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale','stock',],

    # always loaded
    'data': [
        'views/product_template_sediagro_view.xml',
        'views/price_list_view.xml',
        'security/pricelist_security_security.xml',
    ],
    'license': 'LGPL-3',

}