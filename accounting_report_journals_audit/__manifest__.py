# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Accounting Report Audit Journal',
    'version' : '1.1',
    'summary': 'Accounting Report',
    'sequence': 15,
    'description': """
    """,
    'category': 'Invoicing Management',
    'website': '',
    'depends' : ['account','base'],
    'data': [
        'security/ir.model.access.csv',
        'report/journal_report_template.xml',
        'wizard/journals_audit_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
'license': 'LGPL-3',
}
