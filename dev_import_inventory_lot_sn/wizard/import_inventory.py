# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import api, fields, models, _
import base64
import csv
from io import StringIO
from io import BytesIO
from xlwt import easyxf
import xlrd


class dev_import_inventory(models.TransientModel):
    _name = "dev.import.inventory"
    _description = 'Import inventory'


    file_type = fields.Selection([('excel','Excel'),('csv','CSV')],string='File Type', default='csv')
    csv_file = fields.Binary(string='File')
    
    
    
    
    def get_lines(self):
        data=[]
        if self.file_type == 'excel':
            file_datas = base64.decodestring(self.csv_file) 
            workbook = xlrd.open_workbook(file_contents=file_datas)
            sheet = workbook.sheet_by_index(0)
            data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
            data.pop(0)
        else:
            file_data = base64.decodestring(self.csv_file)
            s_data = str(file_data.decode("utf-8")) 
            s_data = s_data.split('\n')
            data =[]
            for d in s_data:
                if d:
                    data.append(d.split(','))
            data.pop(0)
        return data
    
    
    
    def get_serial_number(self,name, product_id):
        lot_pool = self.env['stock.production.lot']
        if name:
            if '.' in name:
                name = name.split('.')[0]
            lot_id = lot_pool.search([('name','=',name),('product_id','=',product_id.id)], limit=1)
            if lot_id:
                return lot_id
#            else:
#                lot_id = lot_pool.create({'name':name, 'product_id':product_id.id})
#                return lot_id.id
            
        return False
    
    
    def import_line(self):
        lines = self.get_lines()
        count=0
        note=''
        for line in lines:
            if line[1] and float(line[1]) > 0.00:
                count += 1
                product_id = self.env['product.product'].search([('default_code','=',line[0])],limit=1)
                stock_inv = self.env['stock.inventory'].browse(self._context.get('active_id'))
                location_id = stock_inv.location_id
                lot_id = False
                if product_id:
                    lot_id = self.get_serial_number(str(line[2]),product_id)
                    if lot_id:
                        vals={
                            'product_id':product_id.id or False,
                            'location_id':location_id.id,
                            'product_qty':line[1] or '',
                            'inventory_id' :stock_inv.id or False,
                            'prod_lot_id':lot_id and lot_id.id or False,
                            
                        }
                        self.env['stock.inventory.line'].create(vals)
                        
                if not product_id:
                    if not note:
                        note = "Product or Lot Not found in uploaded CSV.\n"
                    note += "Line no : "+str(count)+ " Product Code : "+str(line[0])+"\n"
                
                if not lot_id and product_id:
                    if not note:
                        note = "Product or Lot Not found in uploaded CSV.\n"
                    lot_name = str(line[2])
                    if '.' in lot_name:
                        lot_name = lot_name.split('.')[0]
                    note += "Line no : "+str(count)+ " Lot Number : "+ lot_name+"\n"
                
                
                
        if note:
            log_id=self.env['inventory.import.log'].create({'name':note})
            return {
                'view_mode': 'form',
                'res_id': log_id.id,
                'res_model': 'inventory.import.log',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
    
