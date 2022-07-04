# -*- encoding: utf-8 -*-

{
    'name': 'Conciliación Bancaria',
    'version': '1.0',
    'category': 'Contabilidad',
    'description': 'Reporte de conciliación bancaria',
    'author': 'Proyectos Ágiles S. A.',
    'website': 'http://inteligos.gt/',
    'depends': ['base', 'account', 'account_reports'],
    'data': [
        # 'views/account_move_line.xml',
        'views/bank_reconciliation_report.xml',
        'views/bank_reconciliation_wizard.xml',
        'views/inherit_account_views.xml',
        'views/inherit_res_partner.xml',
        'views/send_back_check.xml',
        # 'views/reporte_banco.xml',
        # 'views/reporte_disponibilidad_resumen.xml',
        # 'views/conciliacion_automatica.xml',
        # 'wizard/conciliar.xml',
        # 'wizard/conciliacion_automatica.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
