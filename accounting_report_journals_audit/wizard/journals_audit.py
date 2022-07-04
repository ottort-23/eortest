# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
import xlwt
import xlsxwriter
from xlsxwriter.workbook import Workbook
from io import StringIO
import base64
import os

from itertools import groupby 
from operator import itemgetter
import socket 

class AccountPrintJournalReport(models.TransientModel):
    _name = "account.print.journal.report"
    _description = 'Accounting Report'
    
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    sort_selection = fields.Selection([('date', 'Date'), ('move_name', 'Journal Entry Number'),], 'Entries Sorted by', required=True, default='move_name')
    page_number = fields.Integer("Page Number", default="1")
    excel_file = fields.Binary('excel file')
    file_name = fields.Char('Excel File', size=64)

    
    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] =  False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        result['company_id'] = data['form']['company_id'][0] or False
        return result
    
    def _print_report(self, data):
        report_name='journals_audit_report{}.xls'.format(self.id)
        dir_name = os.path.dirname(__file__)+"/"+report_name
        #path_dir = '/html/accounting_report/'
        #path = '/var/www'+ str(path_dir)

        #file_name = path+report_name
        #if not os.path.exists(path):
        #    os.makedirs(path)
                
        workbook = xlsxwriter.Workbook(dir_name, {'in_memory': True})
        worksheet = workbook.add_worksheet()
#         bold = workbook.add_format({'bold': True})
        row = 5 
        col = 0
        bold = workbook.add_format({ 
                                                'font_size': 10,
                                                'bold': True,
                                                'valign': 'vcenter',
                                                'border': 1,
                                                })
        
        cell_style = workbook.add_format({ 
                                                'font_size': 10,
                                                'valign': 'vcenter',
                                                'border': 1,
                                                })
        
        
        """domain prepartion """
        domain = []
        form =  data.get('form')
        
        date_from =  form.get('date_from')
        date_to =  form.get('date_to')
        target_move = form.get('target_move')
        
        if date_from and date_to:
            domain = [('date','>=',date_from),('date','<=',date_to)]
        if target_move == 'posted':
            domain.append(('move_id.state','=','posted'))
        
        account_move_line_obj = self.env['account.move.line']
        symbol = None
        move_list = []
        account_move_line = account_move_line_obj.search(domain)
        for line in account_move_line:
            line_list = [line.move_id.name,line.account_id.code,line.account_id.name,line.name,
                         line.debit,line.credit,line.move_id.date,line.move_id.ref]
            move_list.append(line_list)
            symbol = line.company_id.currency_id.symbol
        
        row += 1
        for elt, items in groupby(move_list, itemgetter(0,6,7)):
            trans_date = None
            trans_ref = None
            debit_sum = 0.0
            crecit_sum = 0.0
            col = 0
            worksheet.set_column(row, col, 25)
            worksheet.write(row-2, col, "MOVE",bold)
            worksheet.write(row-2, col+1, elt[0] ,bold)
            worksheet.write(row-2, col + 2, "DATE",bold)
            worksheet.write(row-2, col + 3, str(elt[1]),bold)
            worksheet.write(row-1, col, "DESCRPTION",bold)
            worksheet.write(row-1, col+1, elt[2],bold)
            header = ['ACCOUNT','ACCOUNT NAME','LABEL','DEBIT','CREDIT']
            for e in header:
                worksheet.set_column(row, col, 25)
                worksheet.write(row, col, e,bold)
                col += 1
            row += 1
        
            for lst_value in items:
                debit = 0
                credit = 0
                col = 0
                debit_sum = debit_sum + float(lst_value[4])
                crecit_sum = crecit_sum + float(lst_value[5])
                worksheet.write(row, col, lst_value[1],cell_style)
                col = col + 1
                worksheet.write(row, col, lst_value[2],cell_style)
                col = col + 1
                worksheet.write(row, col, lst_value[3],cell_style)
                col = col + 1
#                 if lst_value[4] > 0 :
                debit = str(lst_value[4]) +' '+symbol
                worksheet.write(row, col, debit,cell_style)
                col = col + 1
#                 if lst_value[5] > 0:
                credit = str(lst_value[5]) +' '+symbol
                worksheet.write(row, col, credit,cell_style)
                row = row + 1
            debit_total_with_symbol = str(debit_sum) +' '+symbol
            credit_total_with_symbol = str(crecit_sum) +' '+symbol
            worksheet.write(row, 3, debit_total_with_symbol,bold)
            worksheet.write(row, 4, credit_total_with_symbol,bold)   
            row = row + 4   
            
        workbook.close()
        with open(dir_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        self.write({'excel_file': file_base64,
                    'file_name':'journals_audit_report.xls'})
        
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname_ex(host_name) 
            
        return {'view_mode': 'form',
                    'res_id': self.id,
                    'res_model': 'account.print.journal.report',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': self._context,
                  'target': 'new',
       }
    

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self.with_context(discard_logo_check=True)._print_report(data)
    
    def print_in_pdf(self):
        """
        To get the date and print the report
        @return : return report
        """
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read([])
        res = res and res[0] or {}
        datas['form'] = res
        return self.env.ref('accounting_report_journals_audit.action_journal_report_template').report_action([], data=datas)
    
