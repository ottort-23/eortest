# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.line'

    operations_type = fields.Selection(
        selection=[
            ('NCRE', 'Nota de Crédito'),
            ('NDEB', 'Nota de Débito'),
            ('RnO', 'Retiros no Operados'),
            ('ChR', 'Cheques rechazados'),
            ('InO', 'Interéses no Operados'),
            ('Others', 'Otros')
        ],
        string='Tipo de Operaciones'
    )
    send_back_check = fields.Boolean(
        default=False,
        string="Cheque rechazado"
    )

    def create_send_back_checks(self):
        if self.operations_type == 'ChR' and self.statement_id.state == 'confirm' and not self.send_back_check:
            self.env['send.back.check'].create({
                'bank_statement_line_id': self.id
            })
            self.send_back_check = True


class AccountBankStatementInherited(models.Model):
    _inherit = "account.bank.statement"
    _name = "account.bank.statement"

    total_difference = fields.Monetary(
        copy=False,
        compute="compute_difference_between_balance",
        string="Diferencia de saldos"
    )

    @api.depends('balance_start', 'balance_end_real')
    def compute_difference_between_balance(self):
        for record in self:
            record.total_difference = record.balance_start - record.balance_end_real

    def check_confirm_bank(self):
        super(AccountBankStatementInherited, self).button_confirm_bank()
        for line in self.line_ids:
            line.create_send_back_checks()
