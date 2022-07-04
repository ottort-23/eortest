# -*- coding: utf-8 -*-

from odoo import models,fields


class product_template(models.Model):
    _inherit = "product.template"

    minimum_price = fields.Float("Precio Mínimo")
