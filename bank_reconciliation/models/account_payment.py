# -*- encoding: utf-8 -*-

import logging

from odoo import models, fields, api, tools

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    redeemed_date = fields.Date(string="Fecha Conciliación")

    @api.depends('move_line_ids')
    def _compute_redeemed_date(self):
        for rec in self:
            try:
                bank_statement_line = self.env['account.bank.statement.line'].search(
                    [('journal_entry_ids', 'in', rec.move_line_ids.ids)])
                rec.redeemed_date = bank_statement_line.date
            except Exception as e:
                _logger.error('Hubo un error al agregar la fecha de conciliación del pago según línea de extracto: %s' % (tools.ustr(e)))
