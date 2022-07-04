# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Many2one


class InheritAccountMove(Model):
    """Herencia al Objeto account.move para agregarle
        los campos para las relaciones con region y sub-region para factura
        según el departamento del cliente.
    """
    _inherit = 'account.move'
    _name = 'account.move'

    sub_region_id = Many2one(comodel_name="gt.sub_region",
                             related='partner_id.state_id.sub_region_id',
                             depends=['partner_id.state_id',
                                      'partner_id.state_id.sub_region_id'],
                             store=True, string="Sub-región")
    region_id = Many2one(comodel_name="gt.region",
                         related='partner_id.state_id.sub_region_id.region_id',
                         depends=['partner_id.state_id',
                                  'partner_id.state_id.sub_region_id',
                                  'sub_region_id'],
                         store=True, string="Región")
