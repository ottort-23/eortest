# -*- coding: utf-8 -*-
{
    'name': "Registros por modelo",

    'summary': """
        Listado de los registros de cada modelo""",

    'description': """
        Agrega un botón para mostrar el listado de los registros de cada modelo
    """,

    'author': "Inteligos, S.A.",
    'website': "https://www.inteligos.gt",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'views/ir_model_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}