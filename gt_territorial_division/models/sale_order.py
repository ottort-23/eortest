# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Many2one


class InheritSaleOrder(Model):
    """Herencia al Objeto sale.order para agregarle
        los campos para las relaciones con regiones y sub-regiones para factura y entrega
        según el departamento del  las direcciones de de factura y entrega respectivamente.
    """
    _inherit = 'sale.order'

    sub_region_invoice_id = Many2one(comodel_name="gt.sub_region",
                                     related='partner_invoice_id.state_id.sub_region_id',
                                     depends=['partner_invoice_id.state_id',
                                              'partner_invoice_id.state_id.sub_region_id'],
                                     store=True, string="Sub-región de factura")
    region_invoice_id = Many2one(comodel_name="gt.region",
                                 related='partner_invoice_id.state_id.sub_region_id.region_id',
                                 depends=['partner_invoice_id.state_id',
                                          'partner_invoice_id.state_id.sub_region_id',
                                          'sub_region_invoice_id'],
                                 store=True, string="Región de factura")
    sub_region_shipping_id = Many2one(comodel_name="gt.sub_region",
                                      related='partner_shipping_id.state_id.sub_region_id',
                                      depends=['partner_shipping_id.state_id',
                                               'partner_shipping_id.state_id.sub_region_id'],
                                      store=True, string="Sub-región de entrega")
    region_shipping_id = Many2one(comodel_name="gt.region",
                                  related='partner_shipping_id.state_id.sub_region_id.region_id',
                                  depends=['partner_shipping_id.state_id',
                                           'partner_shipping_id.state_id.sub_region_id',
                                           'sub_region_shipping_id'],
                                  store=True, string="Región de entrega")

