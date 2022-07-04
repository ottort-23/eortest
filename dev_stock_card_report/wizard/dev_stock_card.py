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
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import itertools
from operator import itemgetter
import operator
# ========For Excel========
from io import BytesIO
import xlwt
from xlwt import easyxf
import base64


# =====================


class DevStockCard(models.TransientModel):
    _name = 'dev.stock.card'
    _description = 'Dev Stock Card'

    location_id = fields.Many2one('stock.location', string='Location',
                                  domain="[('usage','=','internal')]", required="1")
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    filter_by = fields.Selection([('product', 'Product'), ('category', 'Product Category')],
                                 string='Filter By', default='product')
    category_id = fields.Many2one('product.category', string='Category')
    product_ids = fields.Many2many('product.product', string='Products')
    company_id = fields.Many2one('res.company', required="1", default=lambda self: self.env.user.company_id)
    excel_file = fields.Binary('Excel File')

    def get_product_ids(self):
        product_pool = self.env['product.product']
        if self.filter_by and self.filter_by == 'product':
            return self.product_ids.ids
        elif self.filter_by and self.filter_by == 'category':
            product_ids = product_pool.search([('type', '=', 'product'), ('categ_id', 'child_of', self.category_id.id)])
            return product_ids.ids
        else:
            product_ids = product_pool.search([('type', '=', 'product')])
            return product_ids.ids

    def in_lines(self, product_ids):
        state = 'done'
        moves = self.env['stock.move'].search(
            [
                ('date', '>=', self.start_date), ('date', '<=', self.end_date),
                ('location_dest_id', '=', self.location_id.id), ('product_id', 'in', tuple(product_ids)),
                ('state', '=', state), ('company_id', '=', self.company_id.id)
            ]
        )

        result = [{'date': move.date.date(), 'origin': move.origin, 'ref': move.reference,
                   'product': move.product_id.product_tmpl_id.name, 'in_qty': move.product_uom_qty,
                   'cost': move.price_unit, 'picking': move.picking_id.name,
                   'product_id': move.product_id.id, 'partner': move.picking_id.partner_id.name,
                   'default_code': move.product_id.default_code,
                   'lots': ", ".join([line.lot_id.name for line in move.move_line_ids.filtered(lambda sml: sml.lot_id)])
                           or ""
                   } for move in moves]


        for res in result:
            total = 0.0
            if res.get('cost'):
                cost = res.get('cost')
                total = cost * res.get('in_qty')
            else:
                cost = 0
            res.update({
                'origin': res.get('ref') if not res.get('origin') else res.get('origin'),
                'out_qty': 0.0,
                'date': res.get('date'),
                'cost': cost,
                'total': total
            })

        return result

    def out_lines(self, product_ids):
        state = 'done'


        moves = self.env['stock.move'].search(
            [
                ('date', '>=', self.start_date), ('date', '<=', self.end_date),
                ('location_id', '=', self.location_id.id), ('product_id', 'in', tuple(product_ids)),
                ('state', '=', state), ('company_id', '=', self.company_id.id)
            ]
        )
        result = [{'date': move.date.date(), 'origin': move.origin, 'ref': move.reference,
                   'product': move.product_id.product_tmpl_id.name, 'out_qty': move.product_uom_qty,
                   'cost': move.price_unit, 'picking': move.picking_id.name,
                   'product_id': move.product_id.id, 'partner': move.picking_id.partner_id.name,
                   'default_code': move.product_id.default_code,
                   'lots': ", ".join([line.lot_id.name for line in move.move_line_ids.filtered(lambda sml: sml.lot_id)])
                           or ""
                   } for move in moves]



        for res in result:
            total = 0.0
            if res.get('cost'):
                cost = res.get('cost') * -1
                total = cost * res.get('out_qty')
            else:
                cost = 0
            res.update({
                'origin': res.get('ref') if not res.get('origin') else res.get('origin'),
                'in_qty': 0.0,
                'date': res.get('date'),
                'cost': cost,
                'total': total
            })

        return result

    def get_opening_quantity(self, product):

        moves_in = self.env['stock.move'].search(
            [
                ('date', '<', self.start_date), ('date', '<', self.end_date),
                ('location_dest_id', '=', self.location_id.id), ('product_id', '=', product),
                ('state', '=', 'done'), ('company_id', '=', self.company_id.id)
            ]
        )
        moves_out = self.env['stock.move'].search(
            [
                ('date', '<', self.start_date), ('date', '<', self.end_date),
                ('location_id', '=', self.location_id.id), ('product_id', '=', product),
                ('state', '=', 'done'), ('company_id', '=', self.company_id.id)
            ]
        )
        qty_in = sum([move.product_qty for move in moves_in])
        qty_out = sum([move.product_qty for move in moves_out])
        qty = qty_in - qty_out
        return qty

    def get_lines(self):
        product_ids = self.get_product_ids()
        result = []
        if product_ids:
            in_lines = self.in_lines(product_ids)
            out_lines = self.out_lines(product_ids)
            lst = in_lines + out_lines
            new_lst = sorted(lst, key=itemgetter('product'))
            groups = itertools.groupby(new_lst, key=operator.itemgetter('product'))
            result = [{'product': k, 'values': [x for x in v]} for k, v in groups]
            for res in result:
                l_data = res.get('values')
                new_lst = sorted(l_data, key=itemgetter('date'), reverse=False)
                res['values'] = new_lst
        return result

    def print_pdf(self):
        data = {'form': self.read()[0]}
        return self.env.ref('dev_stock_card_report.print_stock_card_report').report_action(self, data=None)

    def get_date(self):
        s_date = datetime.strptime(str(self.start_date), '%Y-%m-%d %H:%M:%S').date()
        start_date = s_date.strftime('%d-%m-%Y')
        e_date = datetime.strptime(str(self.end_date), '%Y-%m-%d %H:%M:%S').date()
        end_date = e_date.strftime('%d-%m-%Y')

        data = {'start_date': start_date, 'end_date': end_date}
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
        text_center = easyxf('font:height 200; align: horiz center;'
                             "borders: top thin,left thin,right thin,bottom thin")

        return [main_header_style, left_header_style, header_style, text_left, text_right, text_left_bold,
                text_right_bold, text_center]

    def create_excel_header(self, worksheet, main_header_style, text_left, text_center, left_header_style, text_right,
                            header_style):
        worksheet.write_merge(0, 1, 1, 3, 'Stock Card', main_header_style)
        row = 2
        col = 1
        start_date = datetime.strptime(str(self.start_date), '%Y-%m-%d %H:%M:%S')
        start_date = datetime.strftime(start_date, "%d-%m-%Y ")

        end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strftime(end_date, "%d-%m-%Y ")

        date = 'Desde ' + start_date + ' hasta ' + end_date
        worksheet.write_merge(row, row, col, col + 2, date, text_center)

        row += 2
        worksheet.write(row, 0, 'Ubicación', left_header_style)
        worksheet.write_merge(row, row, 1, 2, self.location_id.display_name, text_left)
        row += 1
        worksheet.write(row, 0, 'Empresa', left_header_style)
        worksheet.write_merge(row, row, 1, 2, self.company_id.name, text_left)
        row += 2

        worksheet.write(row, 0, 'Fecha', left_header_style)
        worksheet.write(row, 1, 'Origen', left_header_style)
        worksheet.write(row, 2, 'Trans. Inventario', left_header_style)
        worksheet.write(row, 3, 'Contacto', left_header_style)
        worksheet.write(row, 4, 'Entradas', header_style)
        worksheet.write(row, 5, 'Salidas', header_style)
        worksheet.write(row, 6, 'Saldo', header_style)
        worksheet.write(row, 7, 'Costo Un.', header_style)
        worksheet.write(row, 8, 'Total', header_style)
        lines = self.get_lines()

        p_group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ivory;'
                               'align: horiz left;font: color black; font:bold True;'
                               "borders: top thin,left thin,right thin,bottom thin")

        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                             'align: horiz left;font: color black; font:bold True;'
                             "borders: top thin,left thin,right thin,bottom thin")

        group_style_right = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                                   'align: horiz right;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin", num_format_str='0.00')

        row += 1
        for line in lines:
            worksheet.write_merge(row, row, 0, 8, line.get('product'), p_group_style)
            row += 1
            count = 0
            balance = 0
            t_in_qty = t_out_qty = 0
            for val in line.get('values'):
                count += 1
                if count == 1:
                    worksheet.write_merge(row, row, 0, 4, 'Saldo Incial', group_style)
                    op_qty = self.get_opening_quantity(val.get('product_id'))
                    balance = op_qty
                    worksheet.write(row, 5, '', group_style_right)
                    worksheet.write(row, 6, op_qty, group_style_right)
                    worksheet.write(row, 7, '', group_style_right)
                    worksheet.write(row, 8, '', group_style_right)
                    row += 1
                balance += val.get('in_qty') - val.get('out_qty')
                t_in_qty += val.get('in_qty')
                t_out_qty += val.get('out_qty')
                worksheet.write(row, 0, val.get('date').strftime('%d/%m/%Y'), text_left)
                worksheet.write(row, 1, val.get('origin'), text_left)
                worksheet.write(row, 2, val.get('picking'), text_left)
                worksheet.write(row, 3, val.get('partner'), text_left)
                worksheet.write(row, 4, val.get('in_qty'), text_right)
                worksheet.write(row, 5, val.get('out_qty'), text_right)
                worksheet.write(row, 6, balance, text_right)
                worksheet.write(row, 7, val.get('cost'), text_right)
                worksheet.write(row, 8, val.get('total'), text_right)
                row += 1
                worksheet.write_merge(row, row, 0, 2, 'Lotes', group_style)
                worksheet.write_merge(row, row, 3, 8, val.get('lots'), group_style)
                row += 1
            worksheet.write_merge(row, row, 0, 3, 'Total', group_style_right)
            worksheet.write(row, 4, t_in_qty, group_style_right)
            worksheet.write(row, 5, t_out_qty, group_style_right)
            worksheet.write(row, 6, balance, group_style_right)
            worksheet.write(row, 7, '-', group_style_right)
            worksheet.write(row, 8, '-', group_style_right)
            row += 2

        row += 1
        return worksheet, row

    def action_generate_excel(self):
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
        filename = 'Kardex.xls'
        worksheet = workbook.add_sheet('Kardex', cell_overwrite_ok=True)
        for i in range(0, 10):
            worksheet.col(i).width = 150 * 30

        worksheet, row = self.create_excel_header(worksheet, main_header_style, text_left, text_center,
                                                  left_header_style, text_right, header_style)

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
                'url': 'web/content/?model=dev.stock.card&download=true&field=excel_file&id=%s&filename=%s' % (
                    active_id, filename),
                'target': 'new',
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
