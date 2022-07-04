# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Char


class ResCurrency(Model):
    """Herencia de objeto para agregar campos para los montos en letras"""
    _inherit = 'res.currency'
    _name = 'res.currency'

    amount_separator = Char(string="Unidad/Subunidad Separador de Texto")
    close_financial_text = Char(string="Cierre Financiero, texto")
