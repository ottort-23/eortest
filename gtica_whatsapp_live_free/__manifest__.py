# -*- coding: utf-8 -*-
# Copyright 2019 GTICA C.A. - Ing Henry Vivas

{
    'name': 'Whatsapp Connect Chat Live',
    'summary': 'Marketing, Sale, connect Chat Whatsapp live for your business',
    'version': '12.0.1.0.0',
    'category': 'Website',
    'author': 'GTICA C.A',
    'support': 'controlwebmanager@gmail.com',
    'license': 'AGPL-3',
    'website': 'http://gtica.online/',
    'price': 0.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'website',
    ],
    'data': [
         'views/res_config_settings.xml',
        'views/view_website_whatsapp.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'gtica_whatsapp_live_free/static/src/scss/gtica_whatsapp.scss',
        ],
    },
    'images': ['static/description/main_screenshot.png'],
    'application': False,
    'installable': True,
}
