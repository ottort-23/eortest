# -*- coding: utf-8 -*-

from calendar import monthrange
from datetime import datetime
from logging import getLogger
import pandas

from odoo.api import model
from odoo.models import AbstractModel
from odoo import tools

_logger = getLogger(__name__)


class ReportPurchaseSaleLedgerReportSoPoLedger(AbstractModel):
    """Clase del tipo Abstracto para crear el reporte Libro de Compras y Ventas"""
    _name = 'report.purchase_sale_ledger.report_so_po_ledger'
    _description = 'Reporte Libro de Compras y Ventas'

    def _get_invoice_id(self, year, month, report_title):
        days = monthrange(int(year), int(month))
        start_date = datetime(int(year), int(month), 1).date()
        end_date = datetime(int(year), int(month), days[1]).date()

        domain = [('doc_type', '!=', 'RECI'),
                  ('date', '>=', start_date),
                  ('date', '<=', end_date)]

        if report_title == 'purchase':
            domain += [('state', 'not in', ['draft', 'cancel']), ('type', 'in', ['in_invoice', 'in_refund'])]
        else:
            domain += [('state', '!=', 'draft'), ('type', 'in', ['out_invoice', 'out_refund'])]

        invoice_ids = self.env['account.move'].search(domain)
        return invoice_ids.sorted(key=lambda r: r.date)  # order by accountable date

    def _get_resume(self, invoices_amount, report_title):
        """RESUMEN"""
        get_resume = lambda list_values: [{key: val for key, val in
                                           zip(['name', 'base_tax', 'exempt', 'amount_tax', 'idp_dai_others', 'total'],
                                               sublist_values)
                                           } for sublist_values in list_values]
        # TODO REVISAR EXENTOS
        """Calculos Base Gravada"""
        goods_base = invoices_amount.get('sub_total_good', 0.00)
        services_base = invoices_amount.get('sub_total_service', 0.00)
        imp_exp_base = invoices_amount.get('sub_total_import_export', 0.00)
        fuel_base = invoices_amount.get('sub_total_idp', 0.00)
        little_contrib_base = invoices_amount.get('sub_total_little_contrib', 0.00)
        ncre_base = invoices_amount.get('sub_total_good_ncre', 0.00) + invoices_amount.get('sub_total_service_ncre',
                                                                                           0.00)
        """Calculos / Base Exenta"""
        goods_exempt = invoices_amount.get('sub_total_goods_exempt_total', 0.00)
        service_exempt = invoices_amount.get('sub_total_service_exempt_total', 0.00)
        imp_exp_exempt = 0.00
        fuel_exempt = 0.00
        little_contrib_exempt = 0.00
        ncre_exempt = invoices_amount.get('sub_total_ncre_exempt_total', 0.00)  # TODO revision ****

        """Calculos Monto IVA"""
        vat_goods = invoices_amount.get('tax_amount_goods', 0.00)
        vat_services = invoices_amount.get('tax_amount_service', 0.00)
        vat_import_export = invoices_amount.get('tax_amount_vat_imp_exp_total', 0.00)  # TODO REVISAR
        vat_fuel = 0.00  # TODO REVISAR
        vat_little_contrib = 0.00
        vat_ncre = invoices_amount.get('tax_amount_goods_total_ncre', 0.00) + invoices_amount.get(
            'tax_amount_services_total_ncre', 0.00)

        """Calculos Monto IDP-DAI-Otros"""
        other_goods = invoices_amount.get('tax_amount_other_good_total', 0.00)
        other_services = invoices_amount.get('tax_amount_other_service_total', 0.00)
        other_import_export = invoices_amount.get('tax_amount_imp_exp', 0.00)
        other_fuel = invoices_amount.get('tax_amount_idp', 0.00)
        other_little_contrib = 0.00
        other_ncre = 0.00

        """Calculos / Suma Total Fila"""
        total_tax_goods = goods_base + goods_exempt + vat_goods + other_goods
        total_tax_services = services_base + service_exempt + vat_services + other_services
        total_tax_imp_exp = imp_exp_base + imp_exp_exempt + vat_import_export + other_import_export
        total_tax_fuel = fuel_base + fuel_exempt + vat_fuel + other_fuel
        total_tax_little_contrib = little_contrib_base + little_contrib_exempt + vat_little_contrib + other_little_contrib
        total_tax_ncre = ncre_base + ncre_exempt + vat_ncre + other_ncre

        """Calculos / Suma Total Columna"""
        base_total = goods_base + services_base + imp_exp_base + fuel_base + little_contrib_base + ncre_base
        total_exempt = goods_exempt + service_exempt + imp_exp_exempt + fuel_exempt + little_contrib_exempt + ncre_exempt
        total_vat = vat_goods + vat_services + vat_import_export + vat_fuel + vat_little_contrib + vat_ncre
        other_total = other_goods + other_services + other_import_export + other_fuel + other_little_contrib + other_ncre
        total = total_tax_goods + total_tax_services + total_tax_imp_exp + total_tax_fuel + total_tax_little_contrib + total_tax_ncre

        """Preparación de datos para darles formato necesario para el reporte."""
        import_export_title = 'IMP' if report_title == 'purchase' else 'EXP'
        lists_values = [['BIENES', goods_base, goods_exempt, vat_goods, other_goods, total_tax_goods],
                        ['SERVICIOS', services_base, service_exempt, vat_services, other_services, total_tax_services],
                        [import_export_title, imp_exp_base, imp_exp_exempt, vat_import_export, other_import_export,
                         total_tax_imp_exp],
                        ['COMBUSTIBLE', fuel_base, fuel_exempt, vat_fuel, other_fuel, total_tax_fuel],
                        ['PEQ. CONTRIBUYENTE', little_contrib_base, little_contrib_exempt, vat_little_contrib,
                         other_little_contrib, total_tax_little_contrib],
                        ['NOTAS-CREDITO', ncre_base, ncre_exempt, vat_ncre, other_ncre, total_tax_ncre],
                        ['TOTAL', base_total, total_exempt, total_vat, other_total, total]]
        resume = get_resume(lists_values)
        return resume

    def _get_taxes_by_type(self, inv_id, inv_line_id, group_type, tax_list):
        inv = self.env['account.invoice'].browse(inv_id)
        inv_line = inv['invoice_line_ids'].browse(inv_line_id)
        tax_lines = inv_line.invoice_line_tax_ids.filtered(lambda line: line.group_type == group_type).ids
        amount_tax = 0.0

        sub_total = inv_line['price_subtotal_signed_2'] \
            if inv_line['currency_id']['name'] == 'USD' else inv_line['price_subtotal']

        for tax_id in tax_lines:
            if tax_id not in tax_list:
                amount_total_tax = sum(inv['tax_line_ids']
                                       .filtered(lambda t: t['tax_id']['id'] == tax_id).mapped('amount_total'))
                amount_total_tax = amount_total_tax * (-1) if amount_total_tax < 0 else amount_total_tax
                amount_total_tax = amount_total_tax / inv['rate_invoice'] \
                    if inv_line['currency_id']['name'] == 'USD' else amount_total_tax
                amount_tax = amount_total_tax
                tax_list.append(tax_id)

        taxes = {'tax_list': tax_list}

        if inv.type == 'out_refund':  # Si el documento es rectificativo
            taxes.update({'ncre_sub_total': sub_total * (-1), 'ncre_amount_tax': amount_tax * (-1)})
        else:
            taxes.update({'sub_total': sub_total, 'amount_tax': amount_tax})
        return taxes

    def _get_tax_calculat(self, invoice_ids, report_title, print_resume):
        """Variables:
            - sub_total_... útiles para montos totales libre de impuestos.
            - tax_amount_..._total útiles para montos totales del impuesto
        """
        sale_or_purchase = report_title in ['sale', 'purchase', 'sales_resume']
        report_headlines = ['FECHA', 'NO.', 'SERIE', 'TIPO DOC.', 'NIT',
                            'NOMBRE', 'IVA', 'TOTAL']
        headline_values = ['goods', 'services', 'vat_tax']

        if sale_or_purchase:
            headline_values[2:2] = ['import_export', 'dai_tax', 'idp', 'idp_tax', 'nvat', 'nvat_tax',
                                    'other', 'other_tax', 'exempt', 'little_contrib']
            report_headlines[6:6] = ['BIENES', 'IMP', 'SERVICIOS', 'EXENTO', 'PEQUEÑO CONTRIB.', 'OTROS']
        elif report_title == 'asistelibros':
            headline_values[2:2] = ['external_goods', 'external_services', 'external_exempt_goods',
                                    'external_exempt_services', 'exempt_goods', 'exempt_services',
                                    'constancy_type', 'constancy_number', 'constancy_amount', 'little_contrib_goods',
                                    'little_contrib_services', 'external_little_contrib_goods',
                                    'external_little_contrib_services']
            report_headlines[0:0] = ['ESTABLECIMIENTO', 'TIPO']
            report_headlines[8:8] = ['TIPO TRANSACCIÓN', 'IDENTIFICACIÓN',
                                     'ESTADO DE DOCUMENTO', 'TIPO DE OPERACION',
                                     'TIPO DE DOCUMENTO DE OPERACION', 'No. TIPO DE DOCUMENTO DE OPERACION',
                                     'TOTAL VALOR GRAVADO DEL DOCUMENTO, BIENES OPERACION LOCAL',
                                     'TOTAL VALOR GRAVADO DEL DOCUMENTO, BIENES OPERACION DEL EXTERIOR',
                                     'TOTAL VALOR GRAVADO DEL DOCUMENTO, SERVICIOS OPERACION LOCAL',
                                     'TOTAL VALOR GRAVADO DEL DOCUMENTO, SERVICIOS OPERACION DEL EXTERIOR',
                                     'TOTAL VALOR EXENTO DEL DOCUMENTO, BIENES OPERACION LOCAL',
                                     'TOTAL VALOR EXENTO DEL DOCUMENTO, BIENES OPERACION DEL EXTERIOR',
                                     'TOTAL VALOR EXENTO DEL DOCUMENTO, SERVICIOS OPERACION LOCAL',
                                     'TOTAL VALOR EXENTO DEL DOCUMENTO, SERVICIOS OPERACION DEL EXTERIOR',
                                     'TIPO DE COONSTANCIA',
                                     'NUMERO DE LA CONSTANCIA DE EXENCIO / ADQUISICION DE INSUMOS / RETENCION DE IVA',
                                     'VALOR DE LA CONSTANCIA DE EXENCIO / ADQUISICION DE INSUMOS / RETENCION DE IVA',
                                     'PEQUEÑO CONTRIBUYENTE TOTAL FACTURADO OPERACION LOCAL BIENES',
                                     'PEQUEÑO CONTRIBUYENTE TOTAL FACTURADO OPERACION LOCAL SERVICIOS',
                                     'PEQUEÑO CONTRIBUYENTE TOTAL FACTURADO OPERACION AL EXTERIOR BIENES',
                                     'PEQUEÑO CONTRIBUYENTE TOTAL FACTURADO OPERACION AL EXTERIOR SERVICIOS']
        sub_total_good = sub_total_good_ncre = sub_total_service = sub_total_service_ncre = \
            sub_total_idp = sub_total_nvat = sub_total_other = sub_total_vat = \
            sub_total_import_export = sub_total_little_contrib = sub_total_service_exempt_total = \
            sub_total_ncre_exempt_total = sub_total_goods_exempt_total = 0.00

        tax_amount_goods_total = tax_amount_goods_total_ncre = tax_amount_imp_exp_total = \
            tax_amount_vat_imp_exp_total = tax_amount_services_total = \
            tax_amount_services_total_ncre = tax_amount_idp_total = \
            tax_amount_vat_fuel_total = tax_amount_nvat_total = \
            tax_amount_other_total = tax_amount_other_good_total = tax_amount_other_service_total = \
            exempt_nvat = exempt_amount_import_export_total = 0.00

        nvat_tax_amount_subtotal_upper = 0.00

        lines = list()
        total_inv = 0
        total_inv_cancelled = len([i for i in invoice_ids
                                   if i['doc_type']
                                   not in ['NCRE', 'PLZ'] and i['state'] == 'cancel'])
        total_ncre = len([i for i in invoice_ids if i['doc_type'] == 'NCRE'])

        for inv in invoice_ids:
            doc_type = inv.doc_type
            line = {key: 0.00 for key in headline_values}

            vat_tax_list, other_tax_list, idp_tax_list, service_tax_list, \
            imp_exp_list, good_tax_list, nvat_tax_list = [], [], [], [], [], [], []

            if inv.state != 'cancel':
                for inv_line in inv.invoice_line_ids:
                    is_a_good = inv_line.product_id.type in ('consu', 'product')
                    is_a_service = inv_line.product_id.type == 'service'

                    if sum(inv_line.invoice_line_tax_ids.mapped('amount')):
                        group_types = inv_line.invoice_line_tax_ids.mapped('group_type')

                        if is_a_good and 'vat' in group_types \
                                and (doc_type != 'PLZ' and not inv.incoterm_id):
                            # IVA tax ---> GOODS
                            goods_taxes = self._get_taxes_by_type(inv['id'], inv_line['id'], 'vat',
                                                                  good_tax_list + service_tax_list)
                            good_tax_list = goods_taxes.get('tax_list', [])
                            line['goods'] += goods_taxes.get('sub_total', goods_taxes.get('ncre_sub_total', 0.00))
                            sub_total_good += goods_taxes.get('sub_total', 0.00) \
                                if 'dai' not in group_types and 'idp' not in group_types else 0.00
                            sub_total_good_ncre += goods_taxes.get('ncre_sub_total', 0.00)  # nuevo
                            line['vat_tax'] += goods_taxes.get('amount_tax', goods_taxes.get('ncre_amount_tax', 0.00))
                            tax_amount_goods_total += goods_taxes.get('amount_tax', 0.00)
                            tax_amount_goods_total_ncre += goods_taxes.get('ncre_amount_tax', 0.00)  # nuevo
                        elif is_a_service and 'vat' in group_types \
                                and (doc_type != 'PLZ' and not inv.incoterm_id):
                            # IVA tax ----> SERVICES
                            services_taxes = self._get_taxes_by_type(inv['id'], inv_line['id'], 'vat',
                                                                     service_tax_list + good_tax_list)
                            service_tax_list = services_taxes.get('tax_list', [])
                            line['services'] += services_taxes.get('sub_total',
                                                                   services_taxes.get('ncre_sub_total', 0.00))
                            sub_total_service += services_taxes.get('sub_total', 0.00) \
                                if 'dai' not in group_types and 'idp' not in group_types else 0.00
                            sub_total_service_ncre += services_taxes.get('ncre_sub_total', 0.00)  # nuevo
                            line['vat_tax'] += services_taxes.get('amount_tax', services_taxes.get('ncre_amount_tax',
                                                                                                   0.00))
                            tax_amount_services_total += services_taxes.get('amount_tax', 0.00)
                            tax_amount_services_total_ncre += services_taxes.get('ncre_amount_tax', 0.00)  # nuevo
                        elif 'vat' in group_types and (
                                doc_type == 'PLZ' or inv.incoterm_id):  # Si el documento es Póliza o si es de exportación o importación
                            # IVA tax ----> PLZ AND IMPORT EXPORT
                            vat_plz_import_export_taxes = self._get_taxes_by_type(inv['id'], inv_line['id'], 'vat', [])
                            line['vat_tax'] += vat_plz_import_export_taxes.get('amount_tax', 0.00)
                            tax_amount_vat_imp_exp_total += vat_plz_import_export_taxes.get('amount_tax',
                                                                                            0.00)  # TODO REVISAR *****

                        if 'dai' in group_types or inv.incoterm_id:
                            # DAI tax ----> IMPORT EXPORT
                            imp_exp_taxes = self._get_taxes_by_type(inv['id'], inv_line['id'], 'dai', imp_exp_list)
                            imp_exp_list = imp_exp_taxes.get('tax_list', [])

                            if sale_or_purchase:
                                line['import_export'] += imp_exp_taxes.get('sub_total', 0.00)
                                line['dai_tax'] += imp_exp_taxes.get('amount_tax', 0.00)
                                tax_amount_imp_exp_total += imp_exp_taxes.get('amount_tax', 0.00)
                            else:
                                key = 'external_goods' if is_a_good else 'external_services'
                                line[key] += imp_exp_taxes.get('sub_total', 0.00)
                            sub_total_import_export += imp_exp_taxes.get('sub_total', 0.00)
                        if 'idp' in group_types and sale_or_purchase:
                            # IDP tax ----> FUEL
                            idp_taxes = self._get_taxes_by_type(inv['id'], inv_line['id'], 'idp', idp_tax_list)
                            idp_tax_list = idp_taxes.get('tax_list', [])
                            line['idp'] += idp_taxes.get('sub_total', 0.00)
                            sub_total_idp += idp_taxes.get('sub_total', 0.00)
                            line['idp_tax'] += idp_taxes.get('amount_tax', 0.00)
                            tax_amount_idp_total += idp_taxes.get('amount_tax', 0.00)
                        if 'nvat' in group_types and report_title == 'sale':
                            # NVAT tax
                            nvat_taxes = self._get_taxes_by_type(inv['id'], inv_line['id'], 'nvat', nvat_tax_list)
                            nvat_tax_list = nvat_taxes.get('tax_list', [])
                            line['nvat'] += nvat_taxes.get('sub_total', 0.00)
                            sub_total_nvat += nvat_taxes.get('sub_total', 0.00)
                            nvat_tax_amount_upper = nvat_taxes.get('amount_tax', 0.00)
                            nvat_tax_amount_subtotal_upper += nvat_taxes.get('amount_tax', 0.00)
                            tax_amount_nvat_total += nvat_taxes.get('amount_tax', 0.00)
                        if 'other' in group_types and sale_or_purchase:
                            # OTHER tax
                            other_taxes = self._get_taxes_by_type(inv['id'], inv_line['id'], 'other', other_tax_list)
                            other_tax_list = other_taxes.get('tax_list', [])
                            line['other'] += other_taxes.get('sub_total', 0.00)
                            sub_total_other += other_taxes.get('sub_total', 0.00)
                            line['other_tax'] += other_taxes.get('amount_tax', 0.00)
                            tax_amount_other_total += other_taxes.get('amount_tax', 0.00)
                            if is_a_good:
                                tax_amount_other_good_total += other_taxes.get('amount_tax', 0.00)
                            elif is_a_service:
                                tax_amount_other_service_total += other_taxes.get('amount_tax', 0.00)
                    else:
                        # EXEMPT
                        exempt_amount_total_excluded_by_inv_line = inv_line.price_subtotal_signed_2 \
                            if inv_line['currency_id']['name'] == 'USD' else inv_line.price_subtotal
                        if sale_or_purchase:
                            if doc_type not in ['FPEQ', 'FCAP']:
                                line['exempt'] += exempt_amount_total_excluded_by_inv_line

                                if doc_type == 'NCRE':
                                    sub_total_ncre_exempt_total += exempt_amount_total_excluded_by_inv_line
                                elif is_a_good and doc_type in ['FACT', 'FCAM']:
                                    sub_total_goods_exempt_total += exempt_amount_total_excluded_by_inv_line
                                elif is_a_service and doc_type in ['FACT', 'FCAM']:
                                    sub_total_service_exempt_total += exempt_amount_total_excluded_by_inv_line
                            elif doc_type in ['FPEQ', 'FCAP']:
                                sub_total_little_contrib += exempt_amount_total_excluded_by_inv_line
                                line['little_contrib'] += exempt_amount_total_excluded_by_inv_line
                        elif report_title == 'asistelibros':
                            if doc_type in ['FPEQ', 'FCAP']:
                                key = 'little_contrib_goods' if is_a_good else 'little_contrib_services'
                            elif doc_type in ['FPEQ', 'FCAP'] and inv.incoterm_id:
                                key = 'external_little_contrib_goods' \
                                    if is_a_good else 'external_little_contrib_services'
                            elif inv.incoterm_id:
                                key = 'external_exempt_goods' if is_a_good else 'external_exempt_services'
                            else:
                                key = 'exempt_goods' if is_a_good else 'exempt_services'
                            line[key] += exempt_amount_total_excluded_by_inv_line
                    # return to report all values
            line.update({'total': sum([value for value in line.values()])})
            new_data = {'date': inv.date_invoice, 'series': inv.fel_serie or inv.doc_serie,
                        'number': inv.fel_number or inv.doc_number,
                        'doc_type': doc_type,
                        'vat': inv.partner_id.vat, 'legal_name': inv.partner_id.legal_name}

            if report_title == 'asistelibros':  # Crear otro módulo para agregar dependencia con punto de venta y evaluar si con inteligs fel.
                move_type = 'V' if inv.type in ['out_invoice', 'out_refund'] else 'C'
                doc_type = ''
                doc_state = 'E' if inv.state in ['done', 'save'] else 'A'
                first_data = {'establishment': inv.company_id.establishment_number,
                              'move_type': move_type, 'doc_type': doc_type}
                operating_values = {
                    # Falta extensión de tipos de documentos para
                    # agregar nuevas formas de mostrar los tipos de docs
                    'transaction_type': inv.transaction_type,
                    'identifier': inv.partner_id.l10n_latam_identification_type_id.name,
                    # Odoo no permite agregar NIT y DPI o # Pasaporte a la vez en los contactos.

                    'doc_state': doc_state if not inv.is_gift_certificate else 'D',
                    # Falta casos en los que se coloca vacío
                    'operating_type': inv.operating_type,
                    'doc_operating_type': inv.doc_operating_type,
                    'number_doc_operating_type': inv.number_doc_operating_type
                }
                line = {k: v for d in [first_data, new_data, operating_values, line] for k, v in d.items()}
            else:
                line.update(new_data)

            lines.append(line)
            total_inv += 1 if doc_type not in ['NCRE', 'PLZ'] else 0

        total_values = {'sub_total_good': sub_total_good,
                        'sub_total_import_export': sub_total_import_export,  # nuevo
                        'sub_total_service': sub_total_service,
                        'sub_total_good_ncre': sub_total_good_ncre,  # nuevo
                        'sub_total_service_ncre': sub_total_service_ncre,  # nuevo
                        'sub_total_idp': sub_total_idp,
                        'sub_total_nvat': sub_total_nvat,
                        'sub_total_other': sub_total_other,  # sin usar
                        'sub_total_vat': sub_total_vat,
                        'sub_total_little_contrib': sub_total_little_contrib,  # nuevo
                        'sub_total_nvat_tax_amount': nvat_tax_amount_subtotal_upper,
                        'sub_total_goods_exempt_total': sub_total_goods_exempt_total,
                        'sub_total_service_exempt_total': sub_total_service_exempt_total,
                        'sub_total_ncre_exempt_total': sub_total_ncre_exempt_total,  # nuevo

                        'untax_nvat': exempt_nvat,  # sin usar
                        'untax_import_export': exempt_amount_import_export_total,  # sin usar

                        'tax_amount_goods': tax_amount_goods_total,
                        'tax_amount_imp_exp': tax_amount_imp_exp_total,
                        'tax_amount_vat_imp_exp_total': tax_amount_vat_imp_exp_total,  # nuevo
                        'tax_amount_service': tax_amount_services_total,
                        'tax_amount_goods_total_ncre': tax_amount_goods_total_ncre,  # nuevo
                        'tax_amount_services_total_ncre': tax_amount_services_total_ncre,  # nuevo
                        'tax_amount_idp': tax_amount_idp_total,
                        'tax_amount_nvat': tax_amount_nvat_total,  # sin usar
                        'tax_amount_other_total': tax_amount_other_total,  # nuevo
                        'tax_amount_other_good_total': tax_amount_other_good_total,  # nuevo
                        'tax_amount_other_service_total': tax_amount_other_service_total,  # nuevo
                        'total_inv': total_inv,
                        'total_inv_cancelled': total_inv_cancelled,
                        'total_ncre': total_ncre}

        resume = self._get_resume(total_values, report_title) if print_resume else []

        if report_title == 'sales_resume':
            """Pandas"""
            df = pandas.DataFrame(lines)
            lines_group_by = df.groupby(['date', 'series'], sort=False).groups
            sale_lines = list()

            def get_sales_resume(data, sale_amounts):
                """
                :param sale_amounts: dict headline values
                :param data: dict data
                :return:
                """
                _logger.info("Objeto data: " + tools.ustr(data))
                _logger.info("Objeto montos de venta resumido: " + tools.ustr(sale_amounts))
                obj_sale = {k: sum([v, sale_amounts[k]]) for k, v in data.items() if k in sale_amounts.keys()}
                return obj_sale

            for key, value in lines_group_by.items():
                _logger.info(
                    "Agrupado por fecha y serie: clave ---> valor" + tools.ustr(key) + ": " + tools.ustr(value))
                sale = {key: 0.00 for key in headline_values}
                for index in value:
                    sale = get_sales_resume(lines[index], sale)

                sale.update({'date': datetime(key[0].year, key[0].month, key[0].day).date(),
                             'series': key[-1], 'total': sum([value for value in sale.values()])})
                sale_lines.append(sale)

            lines = sale_lines
            unwanted_headlines = ['TIPO DOC.', 'NO.', 'NIT', 'NOMBRE']
            report_headlines = [element for element in report_headlines if element not in unwanted_headlines]

        total_values.update({'resume': resume, 'lines': lines, 'headlines': report_headlines})
        _logger.info("Objeto Lines: " + tools.ustr(lines))
        return total_values

    def _get_signed_amounts(self, invoice_ids):
        gtq_invoices = [i for i in invoice_ids if i['currency_id']['name'] == 'GTQ']
        usd_invoices = [i for i in invoice_ids if i['currency_id']['name'] == 'USD']

        for inv in usd_invoices:
            inv['amount_total_signed_2'] = inv['amount_untaxed'] / inv['rate_invoice']  # actualizacion
            for line in inv['invoice_line_ids']:
                line['price_subtotal_signed_2'] = line['price_subtotal'] / inv['rate_invoice']

        gen_invoice_ids = gtq_invoices + usd_invoices
        return gen_invoice_ids

    def _get_first_providers(self, invoice_ids):
        provider_ids = list()
        providers = list()

        for invoice_id in invoice_ids:
            if invoice_id['doc_type'] not in ['NCRE', 'PLZ', 'FPEQ', 'FCAP']:
                partner = invoice_id['partner_id']
                if provider_ids == [] or partner['id'] not in provider_ids:
                    provider_ids.append(partner['id'])
                    provider_invoices = invoice_ids \
                        .filtered(lambda r: r['doc_type'] not in ['NCRE', 'PLZ', 'FPEQ', 'FCAP']) \
                        .filtered(lambda r: r['partner_id'] == partner)
                    provider_invoices = self._get_signed_amounts(provider_invoices)

                    # actualizacion
                    provider_ncre_exempt_docs = invoice_ids \
                        .filtered(lambda r: r['doc_type'] in ['NCRE', 'NABN']) \
                        .filtered(lambda r: r['partner_id'] == partner)
                    provider_ncre_exempt_docs = self._get_signed_amounts(provider_ncre_exempt_docs)

                    amount_total_to_less = sum([inv_line['price_subtotal_signed_2']
                                                if inv['currency_id']['name'] == 'USD' else inv_line['price_subtotal']
                                                for inv in provider_ncre_exempt_docs
                                                for inv_line in inv['invoice_line_ids']
                                                for tax in inv_line['invoice_line_tax_ids']
                                                if inv_line['invoice_line_tax_ids'] if tax['group_type'] == 'vat'])
                    amount_total_to_less += sum([inv_line['price_subtotal_signed_2']
                                                 if inv['currency_id']['name'] == 'USD' else inv_line['price_subtotal']
                                                 for inv in provider_ncre_exempt_docs
                                                 for inv_line in inv['invoice_line_ids']
                                                 if not inv_line['invoice_line_tax_ids']])
                    amount = 0

                    for inv_per_provider in provider_invoices:
                        amount += sum([inv_line['price_subtotal_signed_2']
                                       if inv_per_provider['currency_id']['name'] == 'USD'
                                       else inv_line['price_subtotal']
                                       for inv_line in inv_per_provider.invoice_line_ids
                                       for tax in inv_line['invoice_line_tax_ids']
                                       if inv_line['invoice_line_tax_ids'] if tax['group_type'] == 'vat'])

                    amount_total_provider_invoices = amount
                    amount_total_provider_invoices -= amount_total_to_less
                    providers.append(
                        {'legal_name': partner['legal_name'],
                         'vat': partner['vat'],
                         'qty_invoices': len(provider_invoices),
                         'amount_total': round(amount_total_provider_invoices, 2)
                         }
                    )
        providers.sort(key=lambda p: p['amount_total'], reverse=True)
        return providers[0:10]

    @model
    def _get_report_values(self, docids, data=None):
        year = data['form']['year']
        month = data['form']['month']
        print_resume = data['form']['print_resume']
        report_title = data['form']['ledger_type']
        invoice_ids = self._get_invoice_id(year, month, report_title)
        get_first_providers = self._get_first_providers(invoice_ids)
        gen_invoice_ids = self._get_signed_amounts(invoice_ids)
        get_tax_calculation = self._get_tax_calculat(gen_invoice_ids, report_title, print_resume)
        months = {1: 'Enero', 2: 'Febrero', 3: 'Marzo',
                  4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio',
                  8: 'Agosto', 9: 'Septiembre', 10: 'Octubre',
                  11: 'Noviembre', 12: 'Diciembre'}

        selected_month_name = months[month] if month in months else '***Mes Erróneo***'
        import_export_title = 'IMP' if report_title == 'purchase' else 'EXP'
        first_page_numbr = data['form']['first_page_number']

        return {
            'selected_month': selected_month_name,
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': gen_invoice_ids,
            'data': data,
            'company_id': self.env['res.company'].browse(
                data['form']['company_id'][0]),
            'tax_value': get_tax_calculation,
            'import_export_title': import_export_title,
            'first_page_number': first_page_numbr,
            'providers': get_first_providers,
            'print_resume': print_resume
        }
