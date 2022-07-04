
from odoo import fields, models


class ResCompanyInherit(models.Model):
    _inherit = "res.company"
    _name = "res.company"

    duplicate_nit = fields.Boolean(
        store=True,
        index=True,
        string="¿Existiran NITs duplicados?",
    )
    payment_day = fields.Integer(
        default=4,
        store=True,
        index=True,
        string="Día de pago"
    )

    # todo: para siguiente migración de versión Odoo
    # def _localization_use_documents(self):
    #     self.ensure_one()
    #     if self.country_id.code == "GT":
    #         return True
    #     return super(ResCompanyInherit, self)._localization_use_documents()
