# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ResCompanyInherited(models.Model):
    _inherit = "res.company"

    account_check_printing_layout = fields.Selection(
        string="Formato Cheque", required=True,
        help="Seleccione el formato que desea utilizar para imprimir sus cheques.\n"
             "Para deshabilitar la función, seleccione 'Ninguno'.",
        selection_add=[
            ('action_print_check_voucher', 'Formato'),
            ('action_print_check_format', 'Predeterminado'),
        ],
        default="action_print_check_format",
        ondelete={
            'action_print_check_voucher': 'set default',
            'action_print_check_format': 'set default',
        }
    )
