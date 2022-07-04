# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Amount In Words - Multi Language Supported",
   
    "author": "Softhealer Technologies",
    
    "website": "https://www.softhealer.com",    
    
    "support": "info@softhealer.com",   
    
    "version": "12.0.1",
    
    "category": "Extra Tools",
    
    "summary": "Converts Total Amount into Words for Sales Order, Purchase Order and Invoice.",    

    "description": """Convert Final Amount into Words as per Language of selected Customer/vendor.
        Amount in words available in Form and Report. This module supports Multi Languages.""",
         
    "depends": ['sale_management','purchase'],
    
    "data": [
        "views/amount_in_words.xml", #TODO: BRYAN
        "reports/sale_order_report.xml",        
        "reports/purchase_order_report.xml",        
        "reports/account_invoice_report.xml",        
    ],    
    "images": ["static/description/background.png",],
                 
    "installable": True,
    "auto_install": False,
    "application": True,    
    
    "price": "18",
    "currency": "EUR",
    'license': 'LGPL-3',
}
