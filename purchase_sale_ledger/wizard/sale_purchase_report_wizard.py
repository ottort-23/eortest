# -*- coding: utf-8 -*-

# ========For Excel========
from io import BytesIO
import xlwt
from xlwt import easyxf
import base64
from datetime import datetime
from logging import getLogger
from odoo.models import TransientModel
from odoo.fields import (Selection, Many2one, Integer, Boolean, Binary)
from odoo import tools

_logger = getLogger(__name__)


class SalePurchaseLedgerWizard(TransientModel):
    """Clase del tipo Trasitorio para crear el reporte Libro de Compras y Ventas"""
    _name = "sale.purchase.ledger.wiz"
    _transient = True
    _description = "Wizard Libro de Compras y Ventas"

    def get_years(self):
        year_list = []
        for i in range(2010, 2025):
            year_list.append((str(i), str(i)))
        return year_list

    ledger_type = Selection([('purchase', 'Compras'), ('sale', 'Ventas')], default='purchase')
    company_id = Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    year = Selection(selection=get_years, string='Year', default=datetime.now().year)
    month = Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                              ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                              ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre'), ],
                             string='Month', default=datetime.now().month)
    first_page_number = Integer("Folio Inicial", default=1)
    print_resume = Boolean(default=False, help="Marque si desea imprimir el resumen", string="Imprimir Resumen")
    excel_file = Binary(string='Archivo Excel')

    def get_filter_data(self):
        self.ensure_one()
        data = {}
        res = self.read(['company_id', 'year', 'month', 'first_page_number', 'print_resume', 'ledger_type'])
        res = res and res[0] or {}
        data['form'] = res
        if self.ledger_type == 'purchase':
            data.update({'report_title': 'Libro Compras'})
        else:
            data.update({'report_title': 'Libro Ventas'})
        if self.year:
            data.update({'yyyy': self.year})
        return data

    def get_data(self, filter_data):
        data = self.env['report.purchase_sale_ledger.report_so_po_ledger']._get_report_values([], filter_data)
        return data

    def print_report(self):
        self.ensure_one()
        datas = self.get_filter_data()

        return self.env.ref('purchase_sale_ledger.action_report_so_po_inv_ledger').with_context(
            landscape=True).report_action(self, data=datas)
    """
       Actualización del 21.10.2021
       Mejora para reporte .xls
       """
    """
    EXCEL
        |
        |
        V
    """

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

    def create_main_suppliers(self, worksheet, row, data, main_header_style, text_left, text_center,
                              left_header_style, text_right, header_style, group_style):

        """Encabezados"""
        row += 5
        worksheet.write_merge(row, row, 7, 11, 'Proveedores Primarios', group_style)
        row += 1
        worksheet.write(row, 7, 'Indice', left_header_style)
        worksheet.write(row, 8, 'NIT.', left_header_style)
        worksheet.write(row, 9, 'Proveedor', header_style)
        worksheet.write(row, 10, 'No. Facturas', header_style)
        worksheet.write(row, 11, 'Monto', header_style)
        row += 1
        """Encabezados"""

        """Líneas"""
        providers = data.get('providers')
        for prov in providers:
            index = providers.index(prov) + 1
            worksheet.write(row, 7, index, text_left)
            worksheet.write(row, 8, prov.get('vat'), text_left)
            worksheet.write(row, 9, prov.get('legal_name'), text_right)
            worksheet.write(row, 10, prov.get('qty_invoices'), text_right)
            worksheet.write(row, 11, prov.get('amount_total'), text_right)
            row += 1
        """Líneas"""
        return worksheet, row

    def create_excel_header(self, worksheet, main_header_style, text_left, text_center,
                            left_header_style, text_right, header_style, data):
        """Primeros cambios"""
        selected_month = data.get('selected_month')
        report_title = data.get('data')['form']['ledger_type']
        row = 2
        worksheet.write(row, 0, 'Empresa', left_header_style)
        worksheet.write_merge(row, row, 1, 2, self.company_id.name, main_header_style)
        row += 1
        worksheet.write(row, 0, 'NIT', left_header_style)
        worksheet.write_merge(row, row, 1, 2, self.company_id.vat, main_header_style)
        row += 1
        worksheet.write(row, 0, 'Reporte', left_header_style)
        worksheet.write_merge(row, row, 1, 2, data.get('data').get('report_title'), main_header_style)
        row += 1
        worksheet.write(row, 0, 'Periodo', left_header_style)
        worksheet.write_merge(row, row, 1, 2, selected_month, main_header_style)
        row += 2

        column = 0
        tax_value = data.get('tax_value')
        for headline in tax_value.get('headlines', []):
            worksheet.write(row, column, headline, header_style)
            column += 1

        #
        # p_group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ivory;'
        #                        'align: horiz left;font: color black; font:bold True;'
        #                        "borders: top thin,left thin,right thin,bottom thin")
        #
        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                             'align: horiz left;font: color black; font:bold True;'
                             "borders: top thin,left thin,right thin,bottom thin")

        group_style_right = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                                   'align: horiz right;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin", num_format_str='0.00')
        """Cálculo de monto BIENES, IMP, SERVICE, EXEMPT, LITTLE CONTRIB., IDP, IVA, TOTAL"""
        total_main = 0.00
        total_column = 5
        for inv in tax_value.get('lines', []):
            _logger.info("Objeto line: " + tools.ustr(inv))
            row += 1
            others = inv.get('dai_tax', 0.00) + inv.get('idp_tax', 0.00) + inv.get('other_tax', 0.00)
            row_total_main = inv.get('goods', 0.00) + inv.get('services', 0.00) + inv.get('import_export',
                                                                                          0.00) + inv.get('exempt',
                                                                                                          0.00) + inv.get(
                'little_contrib', 0.00) + others + inv.get('vat_tax', 0.00)
            total_main += row_total_main

            if report_title in ['sale', 'purchase']:
                worksheet.write(row, 0, datetime.strftime(inv.get('date', ''), '%Y-%m-%d'), text_left)
                worksheet.write(row, 1, inv.get('number', False), text_left)
                worksheet.write(row, 2, inv.get('series', False), text_right)
                worksheet.write(row, 3, inv.get('doc_type', False), text_right)
                worksheet.write(row, 4, inv.get('vat', False), text_right)
                worksheet.write(row, 5, inv.get('legal_name', False), text_right)
                worksheet.write(row, 6, inv.get('goods', 0.00), text_right)
                worksheet.write(row, 7, inv.get('import_export', 0.00), text_left)
                worksheet.write(row, 8, inv.get('services', 0.00), text_left)
                worksheet.write(row, 9, inv.get('exempt', 0.00), text_right)
                worksheet.write(row, 10, inv.get('little_contrib', 0.00), text_right)
                worksheet.write(row, 11, others, text_right)
                worksheet.write(row, 12, inv.get('vat_tax', 0.00), text_right)
                worksheet.write(row, 13, row_total_main, text_right)
            elif report_title == 'asistelibros':
                """
                {'establishment': '1', 'move_type': 'V', 'doc_type': '', 'date': datetime.date(2021, 12, 3), 
                 'series': '', 'number': '0002', 'vat': '44653948', 'legal_name': 'Pruebas', 'transaction_type': False, 
                 'identifier': 'VAT', 'doc_state': 'A', 'operating_type': False, 'doc_operating_type': False, 
                 'number_doc_operating_type': False, 'goods': -0.89, 'services': 0.0, 'external_goods': 0.0, 
                 'external_services': 0.0, 'external_exempt_goods': 0.0, 'external_exempt_services': 0.0, 
                 'exempt_goods': 0.0, 'exempt_services': 0.0, 'constancy_type': 0.0, 'constancy_number': 0.0, 
                 'constancy_amount': 0.0, 'little_contrib_goods': 0.0, 'little_contrib_services': 0.0,, 
                 'external_little_contrib_goods': 0.0, 'external_little_contrib_services': 0.0, 
                 'vat_tax': -0.11, 'total': -1.0} 
                """
                worksheet.write(row, 0, inv.get('establishment', False), text_left)
                worksheet.write(row, 1, inv.get('move_type', False), text_right)
                worksheet.write(row, 2, inv.get('doc_type', False), text_right)
                worksheet.write(row, 3, datetime.strftime(inv.get('date', ''), '%Y-%m-%d'), text_left)
                worksheet.write(row, 4, inv.get('series', False), text_right)
                worksheet.write(row, 5, inv.get('number', False), text_right)
                worksheet.write(row, 6, inv.get('vat', False), text_right)
                worksheet.write(row, 7, inv.get('legal_name', False), text_right)
                worksheet.write(row, 8, inv.get('transaction_type', False), text_right)
                worksheet.write(row, 9, inv.get('identifier', False), text_right)
                worksheet.write(row, 10, inv.get('doc_state', False), text_right)
                worksheet.write(row, 11, inv.get('operating_type', False), text_right)
                worksheet.write(row, 12, inv.get('doc_operating_type', False), text_right)
                worksheet.write(row, 13, inv.get('number_doc_operating_type', False), text_right)
                worksheet.write(row, 14, inv.get('goods', 0.00), text_right)
                worksheet.write(row, 15, inv.get('services', 0.00), text_right)
                worksheet.write(row, 16, inv.get('external_goods', 0.00), text_right)
                worksheet.write(row, 17, inv.get('external_services', 0.00), text_right)
                worksheet.write(row, 18, inv.get('external_exempt_goods', 0.00), text_right)
                worksheet.write(row, 19, inv.get('external_exempt_services', 0.00), text_right)
                worksheet.write(row, 20, inv.get('exempt_goods', 0.00), text_right)
                worksheet.write(row, 21, inv.get('exempt_services', 0.00), text_right)
                worksheet.write(row, 22, inv.get('constancy_type', False), text_right)
                worksheet.write(row, 23, inv.get('constancy_number', False), text_right)
                worksheet.write(row, 24, inv.get('constancy_amount', 0.00), text_right)
                worksheet.write(row, 25, inv.get('little_contrib_goods', 0.00), text_right)
                worksheet.write(row, 26, inv.get('little_contrib_services', 0.00), text_right)
                worksheet.write(row, 27, inv.get('external_little_contrib_goods', 0.00), text_right)
                worksheet.write(row, 28, inv.get('external_little_contrib_services', 0.00), text_right)
                worksheet.write(row, 29, inv.get('vat_tax', 0.00), text_right)
                worksheet.write(row, 30, row_total_main, text_right)
            elif report_title == 'sales_resume':
                worksheet.write(row, 0, datetime.strftime(inv.get('date', ''), '%Y-%m-%d'), text_left)
                worksheet.write(row, 1, inv.get('series', False), text_right)
                worksheet.write(row, 2, inv.get('goods', 0.00), text_right)
                worksheet.write(row, 3, inv.get('import_export', 0.00), text_left)
                worksheet.write(row, 4, inv.get('services', 0.00), text_left)
                worksheet.write(row, 5, inv.get('exempt', 0.00), text_right)
                worksheet.write(row, 6, inv.get('little_contrib', 0.00), text_right)
                worksheet.write(row, 7, others, text_right)
                worksheet.write(row, 8, inv.get('vat_tax', 0.00), text_right)
                worksheet.write(row, 9, row_total_main, text_right)

        row += 1
        if report_title != 'asistelibros':
            if report_title == 'sales_resume':
                total_column = 1
            worksheet.write_merge(row, row, 0, total_column, 'Total General', group_style_right)
            total_column += 1
            worksheet.write(row, total_column,
                            tax_value.get('sub_total_good', 0.00) + tax_value.get('sub_total_idp',
                                                                                  0.00) + tax_value.get(
                                'sub_total_good_ncre', 0.00), group_style_right)
            total_column += 1
            worksheet.write(row, total_column, tax_value.get('sub_total_import_export', 0.00), group_style_right)
            total_column += 1
            worksheet.write(row, total_column,
                            tax_value.get('sub_total_service', 0.00) + tax_value.get('sub_total_service_ncre', 0.00),
                            group_style_right)
            total_column += 1
            worksheet.write(row, total_column, tax_value.get('sub_total_goods_exempt_total', 0.00) + tax_value.get(
                'sub_total_service_exempt_total', 0.00), group_style_right)
            total_column += 1
            worksheet.write(row, total_column, tax_value.get('sub_total_little_contrib', 0.00), group_style_right)
            total_column += 1
            worksheet.write(row, total_column,
                            tax_value.get('tax_amount_idp', 0.00) + tax_value.get('tax_amount_imp_exp',
                                                                                  0.00) + tax_value.get(
                                'tax_amount_other_total', 0.00), group_style_right)
            total_column += 1
            worksheet.write(row, total_column,
                            tax_value.get('tax_amount_goods', 0.00) + tax_value.get('tax_amount_vat_imp_exp_total',
                                                                                    0.00) + tax_value.get(
                                'tax_amount_service', 0.00) + tax_value.get('tax_amount_goods_total_ncre',
                                                                            0.00) + tax_value.get(
                                'tax_amount_services_total_ncre', 0.00), group_style_right)
            total_column += 1
            worksheet.write(row, total_column, total_main, group_style_right)
            row += 2

        if report_title == 'Libro Compras':
            worksheet, row = self.create_main_suppliers(worksheet, row, data, main_header_style, text_left, text_center,
                                                        left_header_style, text_right, header_style, group_style)
        if data.get('print_resume'):
            """Encabezados"""
            row += 5
            worksheet.write_merge(row, row, 6, 11, 'Resumen', group_style)
            row += 1
            worksheet.write(row, 6, 'Impuesto', left_header_style)
            worksheet.write(row, 7, 'Base Gravada.', left_header_style)
            worksheet.write(row, 8, 'Base Exenta', header_style)
            worksheet.write(row, 9, 'IVA', header_style)
            worksheet.write(row, 10, 'Otros', header_style)
            worksheet.write(row, 11, 'Total', header_style)
            row += 1
            """Encabezados"""

            """Líneas"""
            for row_resume in tax_value.get('resume', []):
                worksheet.write(row, 6, row_resume.get('name', False), text_left)
                worksheet.write(row, 7, row_resume.get('base_tax', 0.00), text_left)
                worksheet.write(row, 8, row_resume.get('exempt', 0.00), text_right)
                worksheet.write(row, 9, row_resume.get('amount_tax', 0.00), text_right)
                worksheet.write(row, 10, row_resume.get('idp_dai_others', 0.00), text_right)
                worksheet.write(row, 11, row_resume.get('total', 0.00), text_right)
                row += 1
            row += 1
            """Líneas"""

            """Datos adicionales"""
            inv_number = tax_value.get('total_inv', 0)
            cancel_inv_number = tax_value.get('total_inv_cancelled', 0)
            ncre_number = tax_value.get('total_ncre', 0)
            worksheet.write(row, 6, 'Total Facturas', text_center)
            worksheet.write(row, 7, inv_number, text_left)
            row += 1
            worksheet.write(row, 6, 'Total Facturas Anuladas', text_center)
            worksheet.write(row, 7, cancel_inv_number, text_left)
            row += 1
            worksheet.write(row, 6, 'Total Notas Crédito', text_center)
            worksheet.write(row, 7, ncre_number, text_left)
            row += 1
            """Datos adicionales"""
        return worksheet, row

    def print_xls_report(self):
        """Obtención de valores para creación de excel"""
        filter_data = self.get_filter_data()
        data = self.get_data(filter_data)

        if self.ledger_type == 'purchase':
            filename = 'Libro_Compras.xls'
        else:
            filename = 'Libro_Ventas.xls'

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
        worksheet = workbook.add_sheet(data.get('data').get('report_title'), cell_overwrite_ok=True)
        for i in range(0, 10):
            worksheet.col(i).width = 150 * 30

        worksheet, row = self.create_excel_header(worksheet, main_header_style, text_left, text_center,
                                                  left_header_style, text_right, header_style, data)

        # download Excel File
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        excel_file = base64.encodebytes(fp.read())
        fp.close()
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=sale.purchase.ledger.wiz&download=true&field=excel_file&id=%s&filename=%s'
                       % (active_id, filename),
                'target': 'new',
            }
