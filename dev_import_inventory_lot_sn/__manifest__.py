# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

{
    'name': 'Import Inventory With LOT/Serial Number',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Warehouse',
    'description':
        """
        This Module add below functionality into odoo

        1.Import Inventory from CSV File\n
        2.Import Inventory from Excel File\n
		
		import Inventory , import Inventory adjustment line, import Inventory adjustment by csv, import Inventory adjustment by xls, import Inventory adjustment , Inventory adjustment, Inventory adjustment Csv, Inventory adjustment by XLS
Import Inventory adjustment from CSV/XLS
Import inventory from csv
Import inventory from XLS
Import inventory from excel
Import inventory adjustment from csv
Import inventory adjustment from xls
How can import inventory repor
How can import inventory adjustment from CSV
How can import inventory adjustment from XLS
How can import inventory adjustment from excel
Import inventory
import csv, xlsx and xls file to create Inventory adjustments.
import inventory in Inventory module
import the inventory data from file.
Easily create inventory adjustment from excel 
Easily create inventory adjustment from csv
Easily create inventory adjustment from xls
Odoo Import inventory from CSV 
Odoo Import inventory from excel
Odoo Import inventory from xls
Generate inventory adjustment for opening stock.
Import of Inventory using csv / xls with different scenarios
Import inventory using csv/xls with different ways
Import Serial/lot no. with expiry date using csv / xls
Import location using csv / xls
Import inventory adjust line
Import Inventory adjust line easily from excel/csv to odoo	        
Import inventory 
Odoo import inventory 
Import inventory with serial number 
Odoo import inventory with serial number 
Manage import inventory 
Odoo manage import inventory 
Helps you to Import Inventory with Lot number through CSV file or Excel File
Odoo Helps you to Import Inventory with Lot number through CSV file or Excel File
Allows you to import inventory with lot number 
Odoo Allows you to import inventory with lot number 
 Import from CSV or XLS file 
Odoo  Import from CSV or XLS file 
Display log for non-founded product or lot number 
Odoo Display log for non-founded product or lot number 
Manage inventory 
Odoo manage inventory 
        
        
    """,
    'summary': 'odoo app will Import Inventory with lot/serial number',
    'depends': ['sale_stock', 'stock', 'product'],
    'data': [
        'wizard/import_inventory_view.xml',
        'views/inventory_view.xml',
        'wizard/inventory_import_log_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':19.0,
    'currency':'EUR',
    'license': 'LGPL-3',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
