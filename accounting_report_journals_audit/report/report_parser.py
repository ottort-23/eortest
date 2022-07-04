# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from itertools import groupby 
from odoo import api, models,fields
from operator import itemgetter


class report_journal_template(models.AbstractModel):
    _name = 'report.accounting_report_journals_audit.journal_report_template'
    _description = 'journal_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        target_move = data.get('form', {}).get('target_move')
        date_from = data.get('form', {}).get('date_from')
        date_to = data.get('form', {}).get('date_to')
        page_number = data.get('form', {}).get('page_number')
        
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
        move_list = []
        account_move_line = account_move_line_obj.search(domain,
                                                         order="date asc, move_id,debit desc")
        for line in account_move_line:
            line_list = [line.move_id.name,line.account_id.code,line.account_id.name,line.name,
                         line.debit,line.credit,line.move_id.date,line.move_id.ref]
            move_list.append(line_list)
        move_list.sort(key=lambda x: (x[6], x[0], x[4]))
        group_data = groupby(move_list, itemgetter(0,6,7))
        
        elt_list = []
        for elt, items in groupby(move_list, itemgetter(0,6,7)):
            elt_list.append(list(elt))

        return {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': 'account.move.line',
            'data_data':move_list,
            'data': form,
            'group_data':elt_list,
            'self':self,
            'page_number':page_number,
        }

    def get_item(self,data):
        account_move_line_obj = self.env['account.move.line']
        move_line = account_move_line_obj.search([('move_id.name','=',data[0]),('move_id.date','=',data[1]),('move_id.ref','=',data[2])],order='debit desc')
        return move_line
