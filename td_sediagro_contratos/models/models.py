# -*- coding: utf-8 -*-

from odoo import models, fields, api

class td_sediagro_partner(models.Model):
    _inherit = "res.partner"


    contract_ids = fields.One2many("sediagro.contract", "partner_id", "Contratos")

class td_sediagro_contract(models.Model):
    _name = "sediagro.contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre", required = True)
    reference = fields.Char("No. Contrato", required = True)
    greet = fields.Char("Saludos", required = True)
    date_init = fields.Date("Fecha Inicio", required = True)
    date_end = fields.Date("Fecha Final", required = True)
    partner_id = fields.Many2one("res.partner", "Cliente", required = True)
    salesman = fields.Many2one("res.partner", "Vendedor", required = True)
    salesteam = fields.Many2one("crm.team", "Equipo de Venta")
    currency_id = fields.Many2one("res.currency", "Moneda", default=lambda self: self._default_currency_id(), required = True)
    state = fields.Selection(
        [
            ("N","Nuevo"),
            ("A", "Anulado"),
            ("V", "Vigente"),
            ("T", "Terminado"),
            ("C", "Cancelado"),
        ],
        string = "Estado",
        default = 'N'
    )
    line_ids = fields.One2many("sediagro.contract.line","contract_id","Categorias")
    sale_order_ids = fields.One2many("sale.order","contract_id","Ordenes")
    order_count = fields.Integer(compute='_get_order_count',string = "No. Ordenes")
    notes = fields.Text()

    @api.model
    def _default_currency_id(self):
        res_model, res_id = self.env['ir.model.data'].get_object_reference('base', 'USD')
        return self.env[res_model].browse(res_id)

    @api.model
    def create(self, vals):
        vals['name'] = self.env.ref('td_sediagro_contratos.seq_contracts').next_by_id() or 'New'
        result = super(td_sediagro_contract, self).create(vals)
        return result

    
    def _get_order_count(self):
        for contract in self:
            orders = contract.sale_order_ids.search(['&',('state','in',[('sale'),('done')]),('contract_id','=',contract.id)])
            self.order_count = len(orders)

    
    def action_view_contract_orders(self):
        tree_id = self.env.ref("sale.view_order_tree")
        form_id = self.env.ref("sale.view_order_form")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ordenes del Contrato ' + self.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': ['&',('contract_id', '=', self.id),('state','in',[('sale'),('done')])],
            # if you don't want to specify form for example
            # (False, 'form') just pass False
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
            'target': 'current',
        }

    
    def action_confirm(self):
        self.state = 'V'

    
    def action_cancel(self):
        self.state = 'C'

    
    def action_done(self):
        self.state = 'T'

    
    def action_void(self):
        self.state = 'A'

    
    def action_reactivate(self):
        self.state = 'V'

    
    def action_contract_send(self):
        return 0

    
    def print_contract(self):
        return self.env.ref('td_sediagro_contratos.contrato').report_action(self)

    
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.read(['name', 'refernce'])
        return [(contract.id, '%s - %s' % (contract.name,contract.reference))
                for contract in self]

    def _name_search(self, name, args=None, operator='ilike', limit=100):
        if operator == 'like':
            operator = 'ilike'

        versions = self.search(['|',('name', operator, name),('reference', operator, name)], limit=limit)
        return versions.name_get()

class td_sediagro_contract_line(models.Model):
    _name = "sediagro.contract.line"
    _description = 'Lineas de contrato'

    contract_id = fields.Many2one("sediagro.contract","Contrato")
    category_id = fields.Many2one("product.category","Categoria", required = True)
    qty = fields.Integer("Cant. Kg/Lt", required = True)
    price = fields.Float("Precio. Kg/Lt", required = True)
    line_total = fields.Float(compute = '_get_line_total', string = "Importe")
    qty_invoiced = fields.Float(compute = '_get_qty_ordered', string = "Facturado Kg/Lt")
    total_invoiced = fields.Float(compute = '_get_qty_ordered',string="Importe Facturado")
    execution = fields.Float(compute = '_get_execution', string = "% Ejecución")

    
    def _get_line_total(self):
        self.line_total = self.qty * self.price

    @api.depends('qty_invoiced')
    def _get_execution(self):
        for line in self:
            if line.qty > 0:
                line.execution = (line.qty_invoiced / line.qty) * 100
            else:
                line.execution = 0

    
    def _get_qty_ordered(self):
        for line in self:
            total = 0
            total_invoiced = 0
            orders = line.contract_id.sale_order_ids.search(['&',('state','in',[('sale'),('done')]),('contract_id','=',line.contract_id.id)])
            for order in orders:
                for order_line in order.order_line:
                    if order_line.product_id.id == 5945:
                        product_template = self.env['product.template'].search([('id','=',6850)])
                    # REVISAR ESTOS DATOS
                    elif order_line.product_id.id == 1776:
                        product_template = self.env['product.template'].search([('id', '=', 1777)])
                    elif order_line.product_id.id == 6697:
                        product_template = self.env['product.template'].search([('id', '=', 7708)])
                    elif order_line.product_id.id == 6467:
                        product_template = self.env['product.template'].search([('id', '=', 7478)])
                    elif order_line.product_id.id == 4357:
                        product_template = self.env['product.template'].search([('id', '=', 5259)])
                    elif order_line.product_id.id == 5882:
                        product_template = self.env['product.template'].search([('id', '=', 6787)])
                    elif order_line.product_id.id == 2566:
                        product_template = self.env['product.template'].search([('id', '=', 2762)])
                    elif order_line.product_id.id == 6480:
                        product_template = self.env['product.template'].search([('id', '=', 7491)])
                    else:
                        product_template = self.env['product.template'].search([('id', '=', order_line.product_id.id)])
                    # METODO PARA REVISAR QUE LINEAS ESTAN MAL, DESCOMENTAR EN LOCAL PARA VERIFICAR LOS IDS QUE NO ENCUENTRA
                    # if not product_template.categ_id:
                    #     print('ORDER LINE PRODUCT ID', order_line.product_id.id)
                    #     print('ORDER LINE NAME', order_line.product_id.name)
                    if product_template.categ_id == line.category_id:
                        total += order_line.total_kilo_litro
                        total_invoiced += order_line.price_total
                line.qty_invoiced += total    #ToDo: cambiar a qty_delivered
                line.total_invoiced += total_invoiced
                total = total_invoiced = 0




class td_sediagro_contract_product_category(models.Model):
    _inherit = "product.category"

    contract_line_ids = fields.One2many("sediagro.contract.line","category_id","Contratos")

class td_sediagro_contract_sale_order(models.Model):
    _inherit = "sale.order"

    contract_id = fields.Many2one("sediagro.contract", "Contrato")

    @api.onchange('partner_id')
    def _get_contracts(self):
        #return {'domain': {'contract_id': ['&',('partner_id','=',self.partner_id.id),('state','in',[('V')])]}}
        #return {'domain': {'contract_id': ['&', ('partner_id', '=', self.partner_id.id), ('state', '=', 'V')]}}
        #for rec in self:
        return {'domain': {'contract_id': [('partner_id', '=', 12868)]}}

            #return {'domain': {'contract_id': [('partner_id', '=', 12868 rec.partner_id.id)]}}

