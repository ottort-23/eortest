# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    """Check Discount amount."""

    _inherit = "sale.order.line"

    @api.constrains('discount')
    @api.onchange('discount', 'price_unit')
    def _check_discount(self):
        """Actualización del 06/05/2021
            Para poder colocar como dependencia del modulo,
            el modulo sale_coupon y la validación
            if not self.is_reward_line:, pues si el cliente usa cupones o promociones, da un fallo inesperado."""
        for record in self:
            if not record.is_reward_line:
                unit_price = record.price_unit
                if record.discount:
                    discount_amt = False
                    discount_limits = {disc_limit: disc_limit.group_id
                                       for disc_limit in self.env['sales.discount.limit'].search([])}

                    for disc_limit, group in discount_limits.items():
                        if record._uid in group.users.ids:
                            discount_amt = disc_limit.discount

                    if discount_amt and record.discount > discount_amt:
                        raise UserError(
                            _('No esta autorizado para dar descuentos\n'
                              'mayores de %s %%.' % discount_amt))
                    unit_price = unit_price * (1 - (record.discount / 100))

                if record.order_id.currency_id.id != record.order_id.company_id.currency_id.id \
                        and record.order_id.currency_id.rate:
                    unit_price = unit_price / record.order_id.currency_id.rate

                if unit_price < record.product_id.minimum_price:
                    raise UserError(
                        _('El precio de venta es menor al precio mínimo\n'
                          'No puede continuar con la venta.'))
