# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    establishment_number = fields.Integer(
        help="Campo de valor entero, que identifica el # establecimiento. Siendo útil para Facturación FEL",
        string="# de Establecimiento"
    )
    country_id = fields.Many2one(
        'res.country',
        ondelete="cascade",
        store=True,
        default=lambda self: self.company_id.country_id,
        domain="[('code', 'in', ('GT', 'MX', 'SV', 'HN'))]",
        string="País",
        index=True,
        help='Ingrese el país en el que se encuentra el punto de venta.'
    )
    state_id = fields.Many2one(
        'res.country.state',
        ondelete="cascade",
        store=True,
        domain="[('country_id.code', 'in', ('GT', 'MX', 'SV', 'HN'))]",
        string="Departamento",
        index=True,
        help='Ingrese el departamento en el que se encuentra el punto de venta.'
    )
    county_name = fields.Char(
        store=True,
        string="Municipio",
        index=True,
        help='Ingrese el municipio en el que se encuentra el punto de venta.'
    )
    street = fields.Char(
        store=True,
        help="Campo que identifica dirección de establecimiento. Siendo útil para Facturación FEL",
        string="Dirección"
    )
    zip_code = fields.Char(
        store=True,
        help="Campo que identifica el código postal según dirección de establecimiento. "
             "Siendo útil para Facturación FEL",
        string="Código Postal"
    )
