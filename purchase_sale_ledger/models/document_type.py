# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountTax(models.Model):
	_inherit = "account.tax"

	group_type = fields.Selection([('vat','IVA'),
									('nvat','Otros Impuestos de Venta'),
									('idp','IDP'),
									('dai','DAI'),
									('other','Otros Impuestos')],string="Tipo de Impuesto")

