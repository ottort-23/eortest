# -*- encoding: utf-8 -*-

from odoo import api, models
import logging

class ReporteBanco(models.AbstractModel):
    _name = 'report.bank_reconciliation.reporte_banco'

    def lineas(self, conciliadas, datos):
        lineas = []

        cuenta = self.env['account.account'].browse(datos['cuenta_bancaria_id'][0])

        query = [('account_id','=',datos['cuenta_bancaria_id'][0]), '|', '&', ('conciliado_banco','=',False), ('date','<=',datos['fecha_hasta']), '&', ('conciliado_banco','!=',False), ('conciliado_banco.fecha','>',datos['fecha_hasta']) ]
        if conciliadas:
            query = [('account_id','=',datos['cuenta_bancaria_id'][0]), ('conciliado_banco','!=',False), ('conciliado_banco.fecha','>=',datos['fecha_desde']), ('conciliado_banco.fecha','<=',datos['fecha_hasta'])]

        for linea in self.env['account.move.line'].search(query, order='date'):
            detalle = {
                'fecha': linea.date,
                'documento': linea.move_id.name if linea.move_id else '',
                'nombre': linea.partner_id.name or '',
                'concepto': (linea.ref if linea.ref else '') + (linea.name if linea.name else ''),
                'debito': linea.debit,
                'credito': linea.credit,
                'balance': 0,
                'tipo': '',
                'moneda': linea.company_id.currency_id,
            }

            if linea.amount_currency:
                detalle['moneda'] = linea.currency_id
                if linea.amount_currency > 0:
                    detalle['debito'] = linea.amount_currency
                else:
                    detalle['credito'] = -1 * linea.amount_currency

            if not cuenta.currency_id or (linea.currency_id.id == cuenta.currency_id.id):
                lineas.append(detalle)

        balance_inicial = self.balance_inicial(datos)
        if cuenta.currency_id and cuenta.currency_id.id != cuenta.company_id.currency_id.id:
            balance = balance_inicial['balance_moneda']
        else:
            balance = balance_inicial['balance']

        for linea in lineas:
            balance = balance + linea['debito'] - linea['credito']
            linea['balance'] = balance

        return lineas

    def balance_inicial(self, datos):
        self.env.cr.execute('select coalesce(sum(debit) - sum(credit), 0) as balance, coalesce(sum(amount_currency), 0) as balance_moneda from account_move_line l left join bank_reconciliation_fecha f on (l.id = f.move_id) where account_id = %s and fecha < %s', (datos['cuenta_bancaria_id'][0], datos['fecha_desde']))
        return self.env.cr.dictfetchall()[0]

    def movimientos_pendientes(self,datos):
        movimientos = self.env['bank_reconciliation.pendiente'].search([('fecha', '<', datos['fecha_hasta']), ('fecha', '>', datos['fecha_desde']),('account_id', '=', datos['cuenta_bancaria_id'][0])])
        positivos = 0
        negativos = 0
        for movimiento in movimientos:
            if movimiento.monto > 0:
                positivos += movimiento.monto
            else:
                negativos += movimiento.monto
        return {'movimientos_positivos': positivos, 'movimientos_negativos': negativos}

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'moneda': docs[0].cuenta_bancaria_id.currency_id or self.env.user.company_id.currency_id,
            'lineas': self.lineas,
            'balance_inicial': self.balance_inicial(data['form'])['balance_moneda'] if docs[0].cuenta_bancaria_id.currency_id and docs[0].cuenta_bancaria_id.currency_id.id != docs[0].cuenta_bancaria_id.company_id.currency_id.id else self.balance_inicial(data['form'])['balance'],
            'movimientos_pendientes': self.movimientos_pendientes,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
