# -*- coding: utf-8 -*-

from odoo import models, fields


class IrSequenceInherited(models.Model):
    _inherit = 'ir.sequence'
    _name = 'ir.sequence'

    journal_id = fields.Many2one(comodel_name='account.journal', string='Diario')
    l10n_latam_document_type_id = fields.Many2one(comodel_name='l10n_latam.document.type', string='Tipo de documento')
