# -*- coding: utf-8 -*-

from odoo import fields, api, models


class CRMLeadInherit(models.Model):
    _name = "crm.lead"
    _inherit = "crm.lead"

    nit = fields.Char(related="partner_id.vat", string="NIT")
    legal_name = fields.Char(related="partner_id.legal_name", string="Razón Social")
