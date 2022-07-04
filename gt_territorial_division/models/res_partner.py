# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Many2one
from odoo.api import model


class ResPartnerInherited(Model):
    """Herencia al Objeto res.partner para agregarle el campo county_id
        para la relación con el objeto municipio que sustituirá al campo genérico city.
    """
    _inherit = 'res.partner'
    _name = 'res.partner'

    county_id = Many2one(
        'gt.county',
        ondelete="cascade",
        store=True,
        copy=False,
        domain="[('state_id', '=', state_id)]",
        string="Municipio",
        index=True,
        help='Ingrese el municipio para la dirección del cliente.'
    )
    sub_region_id = Many2one(comodel_name="gt.sub_region",
                             related='state_id.sub_region_id',
                             depends=['state_id', 'state_id.sub_region_id'],
                             store=True, string="Sub-región")
    region_id = Many2one(comodel_name="gt.region",
                         related='state_id.sub_region_id.region_id',
                         depends=['state_id', 'state_id.sub_region_id'],
                         store=True, string="Región")

    @model
    def _address_fields(self):
        """Herencia de método para agregar nuevo campo 'county' a los campos de dirección."""
        result = super(ResPartnerInherited, self)._address_fields()
        result.append('county_id')
        return result

    def _prepare_display_address(self, without_company=False):
        """Herencia del método para agregar nuevo valor a los args 'county_name' para el formato de dirección."""
        address_format, args = super(ResPartnerInherited, self)._prepare_display_address(without_company)
        args.update({'county_name': self.county_id.name})

        for key in args.keys():
            if not args.get(key, False):
                address_format.replace('%(' + key + ')s,', '%(' + key + ')s')
        return address_format, args
