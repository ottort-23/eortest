# -*- coding: utf-8 -*-
{
    'name': "División territorial Guatemala",

    'summary': """
        Regiones y subregiones de según departamentos y municipios agrupados en los departamentos respectivos""",

    'description': """
        - Regiones y subregiones geográficas Guatemala según departamentos para evaluar 
        las ventas agrupadas según estos filtros en las busquedas de pedidos, reportes o facturas.
        - Municipios que son agrupados por departamento.
    """,

    'author': "Inteligos, S.A.",
    'website': "http://www.inteligos.gt",
    'category': 'Localization',
    'version': '0.1',
    'depends': ['base', 'sale', 'account', 'contacts', 'l10n_gt_td_generic'],
    'data': [
        'security/ir.model.access.csv',
        'data/gt.county.csv',
        'views/county_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/region_menu.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'LGPL-3'
}
