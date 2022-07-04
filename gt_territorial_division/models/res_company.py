# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Many2one


class ResCompanyInherited(Model):
    """Herencia al Objeto res.company para agregarle el campo county_id para la relación con el objeto municipio
       y de esta manera sustituir el campo genérico city.
    """
    _inherit = 'res.company'
    _name = 'res.company'

    county_id = Many2one(
        'gt.county',
        ondelete="cascade",
        store=True,
        copy=False,
        domain="[('state_id', '=', state_id)]",
        string="Municipio",
        index=True,
        help='Ingrese el municipio para la compañía.'
    )
