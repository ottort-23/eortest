# -*- coding: utf-8 -*-

from odoo import models, api

class ir_model_export(models.Model):
    _inherit = "ir.model"

    def show_tree_view(self):
        self.ensure_one()
        return {
            'name': 'export_' + self.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self.model,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self.env.context,
        }