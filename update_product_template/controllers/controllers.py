# -*- coding: utf-8 -*-
from odoo import http

# class UpdateProductTemplate(http.Controller):
#     @http.route('/update_product_template/update_product_template/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/update_product_template/update_product_template/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('update_product_template.listing', {
#             'root': '/update_product_template/update_product_template',
#             'objects': http.request.env['update_product_template.update_product_template'].search([]),
#         })

#     @http.route('/update_product_template/update_product_template/objects/<model("update_product_template.update_product_template"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('update_product_template.object', {
#             'object': obj
#         })