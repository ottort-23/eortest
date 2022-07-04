# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class SaleOrderInherited(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.partner_invoice_id = self.partner_id.id
        self.partner_shipping_id = self.partner_id.id
