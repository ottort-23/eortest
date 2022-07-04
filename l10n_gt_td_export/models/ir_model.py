# -*- coding: utf-8 -*-

from odoo import models, api


class IrModelExport(models.Model):
    """Extensión de ir.model para agregar función para ver los registros de cada modelo."""
    _inherit = "ir.model"

    def show_tree_view(self):
        """
        :return: action window con los datos necesarios para visualizar los registros de cada modelo.
        """
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
