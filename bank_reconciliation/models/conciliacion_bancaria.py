# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class ConciliacionBancariaPendiente(models.Model):
    _name = "bank_reconciliation.pendiente"
    _description = "Las conciliaciones bancarias importadas que no han sido relacionadas aún"

    date = fields.Date(string="Fecha", required=True)
    account_id = fields.Many2one('account.account', string='Cuenta', required=True)
    journal_id = fields.Many2one('account.journal', string='Diario')
    tipo_documento = fields.Char(string="Tipo doc.", required=True)
    numero_documento = fields.Char(string="No. doc.", required=True)
    monto = fields.Float(string='Monto', required=True)
    tipo_movimiento = fields.Char('Tipo mov.', required=True)

    @api.model
    def conciliables(self, numero_documento, account_id, monto):
        return self.search([('numero_documento', '=', numero_documento), ('account_id', '=', account_id), ('monto', '=', monto)])
