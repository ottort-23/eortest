# -*- encoding: utf-8 -*-

from odoo import api, models, fields
import datetime
import json
import logging

_logger = logging.getLogger(__name__)


class BankReconciliationReport(models.AbstractModel):
    _name = 'report.bank_reconciliation.bank_reconciliation_report'
    _description = 'Reporte de conciliacion de banco'

    #  Androide estuvo aquí
    def get_account_balance(self, journal, data):
        account_balance = 0
        account_ids = tuple(ac for ac in [journal.default_debit_account_id.id, journal.default_credit_account_id.id]
                            if ac)
        if account_ids:
            amount_field = 'aml.balance' if (
                    not journal.currency_id or journal.currency_id == journal.company_id.currency_id) \
                else 'aml.amount_currency'
            query = """SELECT sum(%s) FROM account_move_line aml
                                          LEFT JOIN account_move move ON aml.move_id = move.id
                                          WHERE aml.account_id in %%s AND move.date <= %%s
                                          AND move.state = 'posted';""" % (amount_field,)
            self.env.cr.execute(query, (account_ids, data.date_to,))
            query_results = self.env.cr.dictfetchall()
            if query_results and query_results[0].get('sum') is not None:
                account_balance = query_results[0].get('sum')
        return account_balance

    def get_unredeemed_checks(self, data):
        all_checks = self.env['account.payment'].search(
            [
                ('payment_type', 'in', ['outbound', 'transfer']), ('payment_method_code', '=', 'check_printing'),
                ('journal_id', '=', data.journal_id.id)
            ]
        )
        unredeemed_checks = all_checks. \
            filtered(lambda check: data.date_from <= check.payment_date <= data.date_to and
                                   check.state in ['posted', 'sent'])
        unredeemed_checks_out_of_time = all_checks. \
            filtered(lambda check: check.payment_date < data.date_from and check.payment_date < data.date_to and
                                   check.state in ['posted', 'sent'])
        r = all_checks.filtered(lambda check: check.redeemed_date)
        redeemed_checks_out_of_time = r. \
            filtered(lambda check: (check.payment_date <= data.date_from or check.payment_date <= data.date_to) and
                                   check.state == 'reconciled' and check.redeemed_date > data.date_to)
        checks = unredeemed_checks_out_of_time + unredeemed_checks + redeemed_checks_out_of_time
        return checks.sorted(key=lambda r: r.payment_date)

    def get_unredeemed_transfers(self, data):
        all_transfer = self.env['account.payment'].search(
            [
                ('payment_type', 'in', ['outbound', 'transfer']), ('payment_method_code', '=', 'manual'),
                ('journal_id', '=', data.journal_id.id), ('payment_date', '<=', data.date_to)
            ]
        )
        unredeemed_transfers = all_transfer.filtered(lambda t: t.state in ['posted', 'sent'])
        tr = all_transfer.filtered(lambda transfer: transfer.redeemed_date)
        redeemed_transfer_out_of_time = tr.\
            filtered(lambda t: t.state == 'reconciled' and t.redeemed_date > data.date_to)
        transfers = unredeemed_transfers + redeemed_transfer_out_of_time
        return transfers.sorted(key=lambda r: r.payment_date)

    def get_deposits_in_transit(self, data):
        all_deposits = self.env['account.payment'].search([
            ('payment_type', '=', 'inbound'), ('journal_id', '=', data.journal_id.id)]
        )
        deposits_in_transit = all_deposits. \
            filtered(lambda deposit: data.date_from <= deposit.payment_date <= data.date_to and
                                     deposit.state == 'posted')
        deposits_in_transit_out_of_time = all_deposits. \
            filtered(lambda deposit: deposit.payment_date < data.date_from and deposit.payment_date < data.date_to and
                                     deposit.state == 'posted')
        d = all_deposits.filtered(lambda deposit: deposit.redeemed_date)
        deposits_out_of_time = d. \
            filtered(lambda deposit: (deposit.payment_date <= data.date_from or deposit.payment_date <= data.date_to)
                                     and deposit.state == 'reconciled' and deposit.redeemed_date > data.date_to)
        deposits = deposits_in_transit + deposits_in_transit_out_of_time + deposits_out_of_time
        return deposits.sorted(key=lambda r: r.payment_date)

    def get_multi_transactions(self, data):
        bank_statements = self.env['account.bank.statement'].search(
            [
                ('journal_id', '=', data.journal_id.id), ('state', '=', 'confirm'),
                ('date', '>=', data.date_from), ('date', '<=', data.date_to),
            ]
        )
        multi_transactions = []
        for bank_statement in bank_statements:
            transactions = [transaction for transaction in self.env['account.bank.statement.line'].search(
                [
                    ('operations_type', 'in', ['NCRE', 'NDEB', 'RnO', 'InO', 'Others']),
                    ('statement_id', '=', bank_statement.id)
                ]
            ).sorted(key=lambda t: t.date)]
            multi_transactions += transactions
        return multi_transactions

    def get_data_report(self, data):
        header = {'date_from': datetime.datetime.strftime(data.date_from, '%d/%m/%Y'),
                  'date_to': datetime.datetime.strftime(data.date_to, '%d/%m/%Y')
                  }
        return {'header': header}

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        doc = self.env[model].browse(self.env.context.get('active_id', False))
        journal = self.env['account.journal'].browse(doc.journal_id.id)
        unredeemed_checks = self.get_unredeemed_checks(doc)
        unredeemed_transfers = self.get_unredeemed_transfers(doc)
        deposits_in_transit = self.get_deposits_in_transit(doc)
        multi_transactions = [transaction for transaction in self.get_multi_transactions(doc)
                              if transaction['operations_type'] in ['NCRE', 'NDEB', 'Others']]
        ino_transactions = [transaction for transaction in self.get_multi_transactions(doc)
                            if transaction['operations_type'] == 'InO']
        rno_transactions = [transaction for transaction in self.get_multi_transactions(doc)
                            if transaction['operations_type'] == 'RnO']
        amount_transactions = sum(transaction.amount for transaction in ino_transactions) + \
                              sum(transaction.amount for transaction in rno_transactions) + \
                              sum(transaction.amount for transaction in multi_transactions
                                  if transaction.operations_type in ['NCRE', 'NDEB']) + \
                              sum(transaction.amount for transaction in multi_transactions
                                  if transaction.operations_type == 'Others' and transaction.amount < 0)
        account_balance = self.get_account_balance(journal, doc)
        last_bank_stmt = self.env['account.bank.statement']. \
            search([
            ('journal_id', '=', journal.id), ('accounting_date', '>=', doc.date_from),
            ('accounting_date', '<=', doc.date_to)
        ], order="date desc, id desc", limit=1)
        last_balance = last_bank_stmt and last_bank_stmt[0].balance_end or 0
        report = self.get_data_report(doc)

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'journal': journal,
            'unredeemed_checks': unredeemed_checks,
            'unredeemed_transfers': unredeemed_transfers,
            'deposits_in_transit': deposits_in_transit,
            'multi_transactions': multi_transactions,
            'ino_transactions': ino_transactions,
            'rno_transactions': rno_transactions,
            'amount_transactions': amount_transactions,
            'account_balance': account_balance,
            'last_balance': last_balance,
            'currency': docs[0].journal_id.currency_id or self.env.user.company_id.currency_id,
            'report': report
        }
    #  Androide estuvo aquí

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
