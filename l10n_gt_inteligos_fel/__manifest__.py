# -*- coding: utf-8 -*-
{
    'name': "Emisiones FEL",

    'summary': """
        Implementación FEL en Odoo por Inteligos""",

    'description': """
        Este modulo permite la facturacion FEL de Guatemala para distintos proveedores. Los actualmente integrados son: INFILE
    """,

    'author': "Inteligos, S.A.",
    'website': "http://www.inteligos.gt",
    'category': 'accounting',
    'version': '10.0',

    'depends': ['base', 'account', 'l10n_gt_td_generic', 'gt_territorial_division', 'web_notify'],

    'data': [
        'data/fel_phrases.xml',
        'data/server_action_massive_fel.xml',
        'security/inteligos_fel_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/account_move_view.xml',
        'views/account_journal.xml',
        'views/res_config_settings_account_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
}
