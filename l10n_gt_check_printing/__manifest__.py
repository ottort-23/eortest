# -*- coding: utf-8 -*-
{
    'name': 'Cheques Guatemala',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Impresión de Cheques Guatemala',
    'description': """
Este modulo permite la impresión de cheques voucher para Guatemala.
    """,
    'website': 'https://www.3digital.net',
    'depends' : ['account_check_printing', 'l10n_gt'],
    'data': [
        'data/gt_check_printing.xml',
        'report/print_check.xml',
        'report/print_check_formato.xml',
        'report/report_print_cheque.xml',
        'views/views.xml',
        'views/cheque_setting_view.xml',
        'views/account_vocher_view.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.report_assets_common': [
            'l10n_us_check_printing/static/src/scss/report_check_commons.scss',
            'l10n_us_check_printing/static/src/scss/report_check_bottom.scss',
            'l10n_us_check_printing/static/src/scss/report_check_middle.scss',
            'l10n_us_check_printing/static/src/scss/report_check_top.scss'
        ],
    },
    'installable': True,
    'auto_install': True,
    'license': 'Other proprietary',
}
