# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigAccountInherited(models.TransientModel):
    _inherit = "res.config.settings"
    _name = "res.config.settings"

    mandatory_address_fel = fields.Boolean(
        store=True,
        index=True,
        related="company_id.mandatory_address_fel",
        readonly=False,
        string="¿Ingresar direcciones FEL?",
    )
