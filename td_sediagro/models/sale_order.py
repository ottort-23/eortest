from odoo import models, fields, api

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def apply_domain_payment_term_id(self):
        self.ensure_one()
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            customers = self.env['res.partner'].search([('id', '=',
                                                          self.partner_id.id)])
            res_model, res_id = self.env['ir.model.data'].get_object_reference('account', 'account_payment_term_immediate')
            terms = [res_id]
            for c in customers:
                terms.append(c.property_payment_term_id.id)
            return {
                'domain': {
                    'payment_term_id': [('id', 'in', terms)]
                }}
        else:
            return {
                'domain': {
                    'payment_term_id': [(1, '=', 1)]
                }
            }

    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'payment_term_id': False,
                'fiscal_position_id': False,
            })
            return

        #SI TIENE UN PADRE, TOMAR LOS VALORES DEFAULT DEL PADRE Y NO DEL CONTACTO.
        p = self.partner_id
        if self.partner_id.parent_id:
            p = self.partner_id.parent_id

        addr = p.address_get(['delivery', 'invoice'])
        values = {
            'pricelist_id': p.property_product_pricelist and p.property_product_pricelist.id or False,
            'payment_term_id': p.property_payment_term_id and p.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'user_id': p.user_id.id or p.commercial_partner_id.user_id.id or self.env.uid
        }
        if self.env['ir.config_parameter'].sudo().get_param(
                'sale.use_sale_note') and self.env.user.company_id.sale_note:
            values['note'] = self.with_context(lang=p.lang).env.user.company_id.sale_note

        if p.team_id:
            values['team_id'] = p.team_id.id
        self.update(values)