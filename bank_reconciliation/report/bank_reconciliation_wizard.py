# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

# ========For Excel========
from io import BytesIO
import xlwt
from xlwt import easyxf
import base64


class AsistenteReporteBancoResumido(models.TransientModel):
    _name = 'bank_reconciliation.asistente_reporte_banco_resumido'
    _description = 'Reporte banco resumido'

    journal_id = fields.Many2one(
        'account.journal',
        string='Diario',
        domain="[('type', '=', 'bank')]",
        required=True
    )
    date_from = fields.Date(
        string='Fecha Inicial',
        required=True,
        default=lambda self: datetime.now().strftime('%Y-%m-01')
    )
    date_to = fields.Date(
        string='Fecha Final',
        required=True,
        default=lambda self: datetime.now().strftime('%Y-%m-%d')
    )

    """CAMBIOS EXCEL"""
    excel_file = fields.Binary(string='Archivo Excel')

    def get_filter_data(self):
        """Función para preparar y obtener los datos requeridos
            para ejecutar la acción tipo reporte que genera los valores del informe.
        """
        self.ensure_one()
        data = {
            'ids': [],
            'model': 'bank_reconciliation.asistente_reporte_banco_resumido',
            'form': self.read()[0]
        }
        return data

    def print_report(self):
        data = self.get_filter_data()
        return self.env.ref('bank_reconciliation.bank_reconciliation_action_report') \
            .report_action(self, data=data)

    """CAMBIOS EXCEL
            |
            |
            V
    """

    def get_data(self, filter_data):
        """Función necesaria para llamar el método genérico de Odoo **_get_report_values
            para obtener los valores para crear el reporte.
        :param filter_data: dict con los datos requeridos
            para ejecutar la acción tipo reporte que genera los valores del informe.
        :return: dict con los valores para crear el informe.
        """

        data = self.env['report.bank_reconciliation.bank_reconciliation_report']. \
            with_context(active_model=self._name, active_ids=[self.id], active_id=self.id). \
            _get_report_values([], filter_data)
        return data

    def get_style(self):
        main_header_style = easyxf('font:height 300;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz right;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        left_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz left;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        text_left = easyxf('font:height 200; align: horiz left;')

        text_right = easyxf('font:height 200; align: horiz right;', num_format_str='0.00')

        text_left_bold = easyxf('font:height 200; align: horiz right;font:bold True;')

        text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;', num_format_str='0.00')
        text_center = easyxf('font:height 200; align: horiz center;')

        return [main_header_style, left_header_style, header_style, text_left, text_right, text_left_bold,
                text_right_bold, text_center]

    def create_excel_header(self, worksheet, main_header_style, text_left, text_center,
                            left_header_style, text_right, header_style, data):
        journal = data.get('journal')
        unredeemed_checks = data.get('unredeemed_checks')
        unredeemed_transfers = data.get('unredeemed_transfers')
        deposits_in_transit = data.get('deposits_in_transit')
        multi_transactions = data.get('multi_transactions')
        ino_transactions = data.get('ino_transactions')
        rno_transactions = data.get('rno_transactions')
        amount_transactions = data.get('amount_transactions', 0.00)
        account_balance = data.get('account_balance', 0.00)
        currency = data.get('currency')
        date_from = data.get('report', {}).get('header', {}).get('date_from', '')
        date_to = data.get('report', {}).get('header', {}).get('date_to', '')
        d_from = datetime.strptime(date_from, '%d/%m/%Y')
        d_to = datetime.strptime(date_to, '%d/%m/%Y')

        d_1 = datetime(d_from.year, d_from.month, d_from.day, 00, 00, 00, 00000)
        d_2 = datetime(d_to.year, d_to.month, d_to.day, 00, 00, 00, 00000)

        date_from = datetime.strftime(d_1, '%d/%m/%Y')
        date_to = datetime.strftime(d_2, '%d/%m/%Y')

        """Cálculo de monto para BALANCE DE BANCOS, TOTAL EN CHEQUES NO CONCILIADOS, 
            TOTAL DEPÓSITOS EN TRANSITO, TOTAL TRANSACCIONES RNO, TOTAL TRANSACCIONES INO, 
            TOTAL OTRAS TRANSACCIONES, TOTAL TRANSACCIONES RECTIFICATIVAS, BALANCE CONTABLE DEL REPORTE
        """
        last_bank_balance = data.get('last_balance')
        total_unredeemed_checks = 0.00
        total_unredeemed_transfers = 0.00
        total_deposits_in_transit = 0.00
        total_rno_transactions = 0.00
        total_ino_transactions = 0.00
        total_other_transactions = 0.00
        total_note_transactions = 0.00
        account_balance_report = account_balance - amount_transactions

        p_group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ivory;'
                               'align: horiz center;font: color black; font:bold True;')
        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                             'align: horiz left;font: color black; font:bold True;')
        sign_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                            'align: horiz center;font: color black; font:bold True;'
                            "borders: top thin")

        """Encabezado"""
        report_title = 'REPORTE DE CONCILIACION BANCARIA'
        row = 2
        worksheet.write(row, 0, '', left_header_style)
        worksheet.write_merge(row, row, 0, 4, report_title, main_header_style)
        row += 1
        worksheet.write(row, 0, 'Diario', left_header_style)
        worksheet.write_merge(row, row, 1, 2, journal.name, main_header_style)
        worksheet.write(row, 3, 'Moneda', left_header_style)
        worksheet.write_merge(row, row, 4, 4, currency.name, main_header_style)
        row += 1
        worksheet.write(row, 0, 'Desde', left_header_style)
        worksheet.write_merge(row, row, 1, 2, date_from, main_header_style)
        worksheet.write(row, 3, 'Hasta', left_header_style)
        worksheet.write_merge(row, row, 4, 4, date_to, main_header_style)
        row += 3
        """Encabezado"""

        worksheet.write(row, 0, '', left_header_style)
        worksheet.write(row, 1, 'Saldos', left_header_style)
        worksheet.write(row, 2, '', left_header_style)
        worksheet.write(row, 3, 'Contabilidad', header_style)
        worksheet.write(row, 4, 'Bancos', header_style)

        row += 1
        worksheet.write(row, 0, '', text_left)
        worksheet.write(row, 1, '', text_left)
        worksheet.write(row, 2, '', text_left)
        worksheet.write(row, 3, account_balance_report, text_right)
        worksheet.write(row, 4, last_bank_balance, text_right)

        """Cheques en circulación"""
        row += 2
        worksheet.write(row, 0, '(-)', p_group_style)
        worksheet.write(row, 1, 'Cheques en circulación', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for check in unredeemed_checks:
            row += 1
            worksheet.write(row, 0, datetime.strftime(check.payment_date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, 'Cheque ' + check.document_reference
            if isinstance(check.document_reference, str) else '', text_left)
            worksheet.write(row, 2, check.amount, text_right)
            worksheet.write(row, 3, '', text_right)
            worksheet.write(row, 4, (total_unredeemed_checks + check.amount), text_right)
            total_unredeemed_checks += check.amount
            """Actualización de last_bank_balance"""
            last_bank_balance -= check.amount
        """Cheques en circulación"""

        """Transferencias en circulación"""
        row += 2
        worksheet.write(row, 0, '(-)', p_group_style)
        worksheet.write(row, 1, 'Transferencias en circulación', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for transfer in unredeemed_transfers:
            row += 1
            worksheet.write(row, 0, datetime.strftime(transfer.payment_date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, 'Transferencia ' + transfer.document_reference
            if isinstance(transfer.document_reference, str) else '', text_left)
            worksheet.write(row, 2, transfer.amount, text_right)
            worksheet.write(row, 3, '', text_right)
            worksheet.write(row, 4, (total_unredeemed_checks + transfer.amount), text_right)
            total_unredeemed_transfers += transfer.amount
            """Actualización de last_bank_balance"""
            last_bank_balance -= transfer.amount
        """Transferencias en circulación"""

        """Retiros no Operados"""
        row += 2
        worksheet.write(row, 0, '(-)', p_group_style)
        worksheet.write(row, 1, 'Retiros no Operados', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for withdrawal in rno_transactions:
            row += 1
            worksheet.write(row, 0, datetime.strftime(withdrawal.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, withdrawal.name, text_left)
            worksheet.write(row, 2, withdrawal.amount, text_right)
            worksheet.write(row, 3, (total_rno_transactions + withdrawal.amount), text_right)
            worksheet.write(row, 4, '', text_right)
            total_rno_transactions += withdrawal.amount
            """Actualización de account_balance_report"""
            account_balance_report -= withdrawal.amount
        """Retiros no Operados"""

        """Intereses no Operados"""
        row += 2
        worksheet.write(row, 0, '(+)', p_group_style)
        worksheet.write(row, 1, 'Intereses no Operados', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for interest in ino_transactions:
            row += 1
            worksheet.write(row, 0, datetime.strftime(interest.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, interest.name, text_left)
            worksheet.write(row, 2, interest.amount, text_right)
            worksheet.write(row, 3, (total_ino_transactions + interest.amount), text_right)
            worksheet.write(row, 4, '', text_right)
            total_ino_transactions += interest.amount
            """Actualización de account_balance_report"""
            account_balance_report += interest.amount
        """Intereses no Operados"""

        """Depósito en tránsito"""
        row += 2
        worksheet.write(row, 0, '(+)', p_group_style)
        worksheet.write(row, 1, 'Depósito en tránsito', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for deposit in deposits_in_transit:
            row += 1
            worksheet.write(row, 0, datetime.strftime(deposit.payment_date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, deposit.communication, text_left)
            worksheet.write(row, 2, deposit.amount, text_right)
            worksheet.write(row, 3, '', text_right)
            worksheet.write(row, 4, (total_deposits_in_transit + deposit.amount), text_right)
            total_deposits_in_transit += deposit.amount
            """Actualización de last_bank_balance"""
            last_bank_balance += deposit.amount
        """Depósito en tránsito"""

        """Otros"""
        row += 2
        worksheet.write(row, 0, '(+)(-)', p_group_style)
        worksheet.write(row, 1, 'Otros', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for transaction in multi_transactions:
            row += 1
            worksheet.write(row, 0, datetime.strftime(transaction.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, transaction.name, text_left)
            worksheet.write(row, 2, transaction.amount, text_right)
            worksheet.write(row, 3, transaction.amount, text_right)
            worksheet.write(row, 4, transaction.amount, text_right)

            """Actualización de account_balance_report ó total_note_transactions 
                ó total_other_transactions ó last_bank_balance
            """
            if transaction.operations_type in ['NCRE', 'NDEB']:
                account_balance_report += transaction.amount
                total_note_transactions += transaction.amount
            elif transaction.operations_type == 'Others':
                total_other_transactions += transaction.amount
                if transaction.amount < 0:
                    account_balance_report += transaction.amount
                elif transaction.amount > 0:
                    last_bank_balance += transaction.amount
        """Otros"""

        """Saldo Conciliado"""
        row += 2
        worksheet.write(row, 0, '', group_style)
        worksheet.write(row, 1, '', group_style)
        worksheet.write(row, 2, '', group_style)
        worksheet.write(row, 3, '', group_style)
        worksheet.write(row, 4, '', group_style)

        row += 1
        worksheet.write(row, 0, '', text_right)
        worksheet.write(row, 1, 'Saldo Conciliado', text_center)
        worksheet.write(row, 2, '', text_right)
        worksheet.write(row, 3, account_balance_report, text_right)
        worksheet.write(row, 4, last_bank_balance, text_right)

        row += 1
        worksheet.write(row, 0, '', group_style)
        worksheet.write(row, 1, '', group_style)
        worksheet.write(row, 2, '', group_style)
        worksheet.write(row, 3, '', group_style)
        worksheet.write(row, 4, '', group_style)
        """Saldo Conciliado"""

        """Firmas"""
        row += 6
        worksheet.write_merge(row, row, 0, 1, 'Hecho por', sign_style)
        worksheet.write_merge(row, row, 3, 4, 'Aprobado por', sign_style)
        """Firmas"""

        return worksheet, row

    def print_xls_report(self):
        """Obtención de valores para creación de excel"""
        filter_data = self.get_filter_data()
        data = self.get_data(filter_data)

        filename = 'Conciliacion_Bancaria.xls'

        # ====================================
        # Style of Excel Sheet
        excel_style = self.get_style()
        main_header_style = excel_style[0]
        left_header_style = excel_style[1]
        header_style = excel_style[2]
        text_left = excel_style[3]
        text_right = excel_style[4]
        text_left_bold = excel_style[5]
        text_right_bold = excel_style[6]
        text_center = excel_style[7]
        # ====================================

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(filename, cell_overwrite_ok=True)
        for i in range(0, 10):
            worksheet.col(i).width = 300 * 30

        worksheet, row = self.create_excel_header(worksheet, main_header_style, text_left, text_center,
                                                  left_header_style, text_right, header_style, data)

        # download Excel File
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        excel_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=bank_reconciliation.asistente_reporte_banco_resumido&download=true&field'
                       '=excel_file&id=%s&filename=%s' % (
                           active_id, filename),
                'target': 'new',
            }

    """CAMBIOS EXCEL"""
