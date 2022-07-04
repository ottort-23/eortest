# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class product_template(models.Model):
    _inherit = 'product.template'

    composicion = fields.Text(string = 'Composición')
    dosis = fields.Float("Dosis")
    origen = fields.Char('País Origen')
    kilo_litro = fields.Float("Kilo / Litro")


class AccountInvoiceLineInherited(models.Model):
    _inherit = "account.move.line"

    #TODO BRYAN
    def name_get(self):
        return [(line.id, '[%s] %s' % (line.product_id.kilo_litro * line.quantity, line.name))
                for line in self]


class order_line_dose(models.Model):
    _inherit = 'sale.order.line'

    dose_ha = fields.Float("Dosis/Ha")
    cost_ha = fields.Float(compute='_get_cost_ha',string = "Costo/Ha (Kg/Lt)")
    total_kilo_litro = fields.Float(compute='_get_cost_ha', string="Total Kg/Lt")
    total_kilo_litro_delivered = fields.Float(compute='_get_cost_ha', string="Total Kg/Lt")
    # price_min = fields.Float('Min Price', store=True, digits=dp.get_precision('Product Price'), compute='_get_cost_ha')

    @api.onchange('product_id','price_unit','product_uom_qty')
    def _get_cost_ha(self):
        for record in self:
            if record.product_id:
                # products = self.env['product.template'].search([('id',"=",record.product_id.id)])
                # for product in products:
                #     if product:
                #record.dose_ha = 0
                record.cost_ha = 0
                record.total_kilo_litro = 0
                product = record.product_id
                if product.kilo_litro > 0:
                    if record.dose_ha != 0:
                        record.dose_ha = record.dose_ha
                    else:
                        record.dose_ha = product.dosis
                    record.cost_ha = record.dose_ha * (record.price_unit / product.kilo_litro)
                    record.total_kilo_litro = product.kilo_litro * record.product_uom_qty
                    record.total_kilo_litro_delivered = product.kilo_litro * record.qty_delivered

    @api.onchange('dose_ha')
    def _get_cost_ha_dose(self):
        prod_obj = self.env['product.template']
        for record in self:
            if record.product_id:
                products = prod_obj.search([('id', "=", record.product_id.id)])
                for product in products:
                    if product:
                       # record.dose_ha = 0
                        record.cost_ha = 0
                        record.total_kilo_litro = 0
                        if product.kilo_litro > 0:
                            if record.dose_ha != 0:
                                record.dose_ha = record.dose_ha
                            else:
                                record.dose_ha = product.dosis
                            record.cost_ha = record.dose_ha * (record.price_unit / product.kilo_litro)
                            record.total_kilo_litro = product.kilo_litro * record.product_uom_qty


class stock_picking_dose(models.Model):
    _inherit = 'stock.move.line'

    total_kilo_litro_initial = fields.Float(compute='_get_total_kilo_litro', string="Total Kg/Lt Inicial")
    total_kilo_litro_done = fields.Float(compute='_get_total_kilo_litro', string="Total Kg/Lt Hecho", store=True)

    @api.onchange('product_id','product_uom_qty','quantity_done')
    
    def _get_total_kilo_litro(self):
        for record in self:
            if record.product_id:
                product = self.env['product.template'].browse(record.product_id.product_tmpl_id.id)
                if product:
                    record.total_kilo_litro_initial = product.kilo_litro * record.product_uom_qty
                    record.total_kilo_litro_done = product.kilo_litro * record.qty_done
                else:
                    record.total_kilo_litro = 0

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    total_kilo_litro = fields.Float(compute='_get_total_kilo_litro', string="Total Kg/Lt")

    @api.onchange('product_id','product_qty')

    def _get_total_kilo_litro(self):
        for record in self:
            if record.product_id:
                product = self.env['product.template'].browse(record.product_id.product_tmpl_id.id)
                if product:
                    record.total_kilo_litro = product.kilo_litro * record.product_qty
                else:
                    record.total_kilo_litro = 0


class stock_move_dose(models.Model):
    _inherit = 'stock.move'

    total_kilo_litro_initial = fields.Float(compute='_get_total_kilo_litro', string="Total Kg/Lt")
    total_kilo_litro_done = fields.Float(compute='_get_total_kilo_litro', string="Total Kg/Lt")

    @api.onchange('product_id','product_uom_qty','quantity_done')
    def _get_total_kilo_litro(self):
        for record in self:
            if record.product_id:
                product = self.env['product.template'].browse(record.product_id.product_tmpl_id.id)
                if product:
                    record.total_kilo_litro_initial = product.kilo_litro * record.product_uom_qty
                    record.total_kilo_litro_done = product.kilo_litro * record.quantity_done
                else:
                    record.total_kilo_litro = 0


class user_analytic_account(models.Model):
    _inherit = 'res.users'

    analytic_account_id = fields.Many2one("account.analytic.account", "Cuenta Analitica")


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.onchange('user_id')
    def _set_analytic_account(self):
        if self.user_id:
            self.analytic_account_id = self.user_id.analytic_account_id