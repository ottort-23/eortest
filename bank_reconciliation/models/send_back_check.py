# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class SendBackCheck(models.Model):
    _name = 'send.back.check'
    _description = 'Envio de cheque'

    name = fields.Char(
        copy=False,
        related="bank_statement_line_id.name",
        string="Descripción"
    )
    ref = fields.Char(
        copy=False,
        related="bank_statement_line_id.ref",
        string="Referencia"
    )
    amount = fields.Monetary(
        copy=False,
        related="bank_statement_line_id.amount",
        string="Monto"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        copy=False,
        related="bank_statement_line_id.partner_id",
        string="Cliente"
    )
    date = fields.Date(
        copy=False,
        related="bank_statement_line_id.date",
        string="Fecha"
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        copy=False,
        related="bank_statement_line_id.currency_id",
        string="Moneda"
    )
    account_number = fields.Char(
        copy=False,
        related="bank_statement_line_id.account_number",
        string="Número de Cuenta"
    )
    bank_statement_line_id = fields.Many2one(
        comodel_name="account.bank.statement.line",
        copy=False,
        string="Línea Extracto bancario"
    )
    bank_statement_id = fields.Many2one(
        comodel_name="account.bank.statement",
        copy=False,
        related="bank_statement_line_id.statement_id",
        string="Extracto bancario"
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        related='bank_statement_line_id.company_id',
        string='Compañía',
        store=True
    )
