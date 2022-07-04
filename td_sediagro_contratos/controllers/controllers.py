# -*- coding: utf-8 -*-
from odoo import http

# class TdSediagroContratos(http.Controller):
#     @http.route('/td_sediagro_contratos/td_sediagro_contratos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/td_sediagro_contratos/td_sediagro_contratos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('td_sediagro_contratos.listing', {
#             'root': '/td_sediagro_contratos/td_sediagro_contratos',
#             'objects': http.request.env['td_sediagro_contratos.td_sediagro_contratos'].search([]),
#         })

#     @http.route('/td_sediagro_contratos/td_sediagro_contratos/objects/<model("td_sediagro_contratos.td_sediagro_contratos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('td_sediagro_contratos.object', {
#             'object': obj
#         })