# -*- coding: utf-8 -*-

# Created on 2019-01-04
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Odoo12在线用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/12.0/en/index.html

# Odoo12在线开发者手册（长期更新）
# https://www.sunpop.cn/documentation/12.0/index.html

# Odoo10在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/

{
    'name': 'App Product Weight Auto Set',
    'version': '12.19.03.04',
    'summary': 'Auto set Product weight if the UoM is in Weight Category. Can be use in sale, purchase, stock',
    'sequence': 10,
    'license': 'LGPL-3',
    'description': """
    All in one Weight solution for sale, purchase, purchase agreement, mrp, stock.
    Auto Set Product Weight, weight auto.
    eg: set UoM='t', then auto set weight='1000kg'.
    set UoM='lb(s)', then auto set weight='0.45kg'.
    Better use with [app_product_weight_sale] together
    """,
    'category': 'Sales',
    'author': 'Sunpop.cn',
    'website': 'https://www.sunpop.cn',
    'images': ['static/description/banner.png'],
    'currency': 'EUR',
    'price': 38,
    'depends': [
        'product'
    ],
    'data': [
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
