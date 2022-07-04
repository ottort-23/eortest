# -*- coding: utf-8 -*-
{
    'name': "db_clean",
    'license': 'LGPL-3',
    'summary': """
        Limpieza de registros de tablas Odoo.""",

    'description': """
        Limpieza de registros de tablas Odoo de forma controlada y especifica.
    """,

    'author': "Proyectos Ágiles S. A.",
    'website': "http://www.inteligos.gt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/app_theme_config_settings_views.xml',
        'data/res_groups.xml',
    ],
}
