
from odoo import fields, api, models, _


class AccountAccountInherited(models.Model):
    _inherit = "account.account"
    _name = "account.account"

    """Actualización Androide, 15/03/2021
        Campo para filtrar cuenta contable personalizada de destino en pagos. 
        Si no es seleccionada esta opción, no tomará esta cuenta 
        como posible selección en el campo cuenta de destino en pagos.
    """
    is_custom_payment_account = fields.Boolean(
        copy=False,
        index=True,
        help="Campo para filtrar cuenta contable personalizada de destino en pagos. "
             "Si no es seleccionada esta opción, no tomará esta cuenta "
             "como posible selección en el campo cuenta de destino en pagos.",
        string="Es cuenta de destino para pagos"
    )
