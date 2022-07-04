from odoo import models, fields, api

# class price_list_access(models.Model):
#     _inherit = 'res.users'
#
#     pricelist_ids = fields.Ma2many('product.pricelist','user_ids','Listas de Precios')


class users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    pricelist_ids = fields.Many2many('product.pricelist', 'pricelist_security_pricelist_users','user_id','pricelist_id', 'Restricted Pricelists', help="This Pricelists and the information related to it will be only visible for users where you specify that they can see them setting this same field.")

class product_pricelist_user(models.Model):
    _name = 'product.pricelist'
    _inherit = 'product.pricelist'

    user_ids = fields.Many2many('res.users', 'pricelist_security_pricelist_users', 'pricelist_id',
                                'user_id', string='Restricted to Users',
                                help='If choose some users, then this Pricelist and the information related to it will be only visible for those users.')