# -*- coding: utf-8 -*-

{
    'name': "Sale Discount Limit",
    'summary': """
            Sale Discount Limit based on Sales User Access Right.
             """,
    'description': """
        Sale Discount Limit based on Sales User Access Right.
        Like Sales Manager can giver maximum 15% Discount,
        Sales User can give maximum 10% Discount.
    """,
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'license': "AGPL-3",
    'category': 'Sales',
    'version': '10.0.1.0.0',
    'depends': ['sale', 'sale_coupon'],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_discount_limit_view.xml',
        'views/product_template_view.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'post_init_hook': '_fill_sales_discount_limit',
}
