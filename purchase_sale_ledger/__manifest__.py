{
    'name': 'Libro de Compras y Ventas',
    'version': '6.0',
    'category': 'Accounting',
    'description': "It has to differ VAT taxes from all other taxes.",
    'author': 'Inteligos, S.A.',
    'company': 'Inteligos, S.A.',
    'maintainer': 'Inteligos, S.A.',
    'depends': ['account', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'views/document_type_view.xml',
        'wizard/sale_purchase_report_wiz.xml',
        'report/header_footer_report.xml',
        'report/sale_po_ledger_report.xml',
        'report/report_sale_purchase_ledger.xml',
    ],
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['pandas']
    },
    'installable': True,
    'application': False,
    'auto_install': True,
}
