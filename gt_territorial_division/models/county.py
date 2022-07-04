# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import (Char, Many2one)


class GTCounty(Model):
    """Objeto para los registros municipios geográficos Guatemala
        que serán necesarios y útiles en lugar de el campo genérico Odoo city.
        Serán agrupados en los respectivos departamentos.
    """
    _name = "gt.county"
    _description = "Municipio geográfico de Guatemala"

    name = Char(
        store=True,
        index=True,
        copy=False,
        required=True,
        string="Nombre",
        help='Ingrese el nombre del municipio'
    )
    state_id = Many2one(
        'res.country.state',
        ondelete="cascade",
        store=True,
        copy=False,
        domain="[('country_id.code', '=', 'GT')]",
        string="Departamento",
        index=True,
        help='Ingrese el departamento al que pertenece el municipio'
    )
