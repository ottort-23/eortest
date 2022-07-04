# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartnerInherited(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    send_back_check_ids = fields.One2many(
        comodel_name="send.back.check",
        inverse_name="partner_id",
        copy=False,
        string='Cheques rechazados'
    )
    count_send_back_check = fields.Integer(
        copy=False,
        compute="_compute_count_send_back_check",
        string="Cantidad de cheques rechazados"
    )

    @api.depends('send_back_check_ids')
    def _compute_count_send_back_check(self):
        for rec in self:
            rec['count_send_back_check'] = len(rec.send_back_check_ids)

    def action_view_send_back_checks(self):
        view = self.env.ref('bank_reconciliation.tree_view_send_back_check')
        partner_id = self.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cheques rechazados de ' + self.name,
            'view_type': 'form',
            'res_model': 'send.back.check',
            'domain': [('partner_id', '=', partner_id)],
            'view_id': view.id,
            'views': [(view.id, 'tree')],
            'target': 'new',
        }
