# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date, datetime
from odoo import api, fields, models, tools, _


class PosCloseSessionReport(models.TransientModel):
    _name = 'close.session.report.wiz'
    _description = 'Reporte de cierre de sesion'

    pos_session_ids = fields.Many2many('pos.session', string="Sesión(es) POS",
                                       domain="[('state', 'in', ['closed'])]", required=True)
    report_type = fields.Char('Tipo de Reporte', readonly=True, default='PDF')
    company_id = fields.Many2one('res.company', "Compañía")

    
    def generate_close_session_report(self):
        data = {'session_ids': self.pos_session_ids.ids,
                'company': self.company_id.id}
        return self.env.ref('bi_pos_closed_session_reports.action_close_session_report_print').report_action([],
                                                                                                             data=data)


class ClosedSessionReport(models.AbstractModel):
    _name = 'report.bi_pos_closed_session_reports.report_closed_session'
    _description = 'Closed Session Point of Sale Details'

    @api.model
    def get_sale_details(self, sessions=False, company=False):
        if sessions:
            orders = self.env['pos.order'].search([
                ('session_id.state', 'in', ['closed']),
                ('session_id', 'in', sessions.ids)])

        user_currency = self.env.user.company_id.currency_id

        total = 0.0
        products_sold = {}
        total_tax = 0.0
        taxes = {}
        mypro = {}
        products = []
        categories_data = {}
        total_discount = 0.0
        return_total = 0.0
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id._convert(
                    order.amount_total, user_currency, order.company_id, order.date_order or fields.Date.today())
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            total_tax = total_tax + order.amount_tax
            for line in order.statement_ids:
                if 'return' in line.name:
                    return_total += abs(line.amount)

            for line in order.lines:
                total_discount += line.qty * line.price_unit - line.price_subtotal

                category = line.product_id.pos_categ_id.name
                if category in categories_data:
                    old_subtotal = categories_data[category]['total']
                    categories_data[category].update({
                        'total': old_subtotal + line.price_subtotal_incl,
                    })
                else:
                    categories_data.update({category: {
                        'name': category,
                        'total': line.price_subtotal_incl,
                    }})

            categories_tot = list(categories_data.values())
        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
        if st_line_ids:
            self.env.cr.execute("""
				SELECT aj.name, sum(amount) total
				FROM account_bank_statement_line AS absl,
					 account_bank_statement AS abs,
					 account_journal AS aj 
				WHERE absl.statement_id = abs.id
					AND abs.journal_id = aj.id 
					AND absl.id IN %s 
				GROUP BY aj.name
			""", (tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        sessions_name = []
        opening_balance = 0.0
        clsoing_balance = 0.0
        control_diff = 0.0
        open_session = sessions[0]
        last_session = sessions[-1]

        for line in open_session.statement_ids:
            if line.journal_id.type == 'cash':
                opening_balance = line.balance_start

        for line in last_session.statement_ids:
            if line.journal_id.type == 'cash':
                clsoing_balance = line.balance_end_real
                control_diff = line.difference

        for i in sessions:
            sessions_name.append(i.name)

        num_sessions = ', '.join(map(str, sessions_name))

        return {
            'currency_precision': 2,
            'total_paid': user_currency.round(total),
            'payments': payments,
            'company_name': self.env.user.company_id.name,
            'taxes': float(total_tax),
            'num_sessions': num_sessions,
            'categories_data': categories_tot,
            'total_discount': total_discount,
            'print_date': datetime.now(),
            'return_total': return_total,
            'opening_balance': opening_balance,
            'clsoing_balance': clsoing_balance,
            'control_diff': control_diff,
            'company': company,
        }

    
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        sessions = self.env['pos.session'].search([('id', 'in', data['session_ids'])], order='id asc')
        company = self.env['res.company'].browse(data['company'])
        data.update(self.get_sale_details(sessions, company))
        return data
