# -*- coding: utf-8 -*-
{
    'name': "fel_pos",

    'summary': """
        FEL para POS""",

    'description': """
        Facturación FEL para Puntos de Venta, imprimiendo datos Fel desde el POS.
    """,

    'author': "Proyectos Ágiles S. A.",
    'website': "http://www.inteligos.gt",
    'category': 'Facturación PoS',
    'version': '0.1',
    'depends': ['base', 'point_of_sale', 'l10n_gt_inteligos_fel', 'product'],
    'data': [
        #'views/assets.xml',
        'views/inherit_config_pos_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fel_pos/static/src/js/models.js',
            'fel_pos/static/src/js/screens.js'
        ],
        'web.assets_qweb': [
            'fel_pos/static/src/xml/*.xml',
        ],
    },
    'installable': True,
    'auto_install': True,
    'application': True,
    'license': 'LGPL-3',
}
