# -*- coding: utf-8 -*-
from odoo import http

# class StockDiferenceJarochito(http.Controller):
#     @http.route('/stock_diference_jarochito/stock_diference_jarochito/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_diference_jarochito/stock_diference_jarochito/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_diference_jarochito.listing', {
#             'root': '/stock_diference_jarochito/stock_diference_jarochito',
#             'objects': http.request.env['stock_diference_jarochito.stock_diference_jarochito'].search([]),
#         })

#     @http.route('/stock_diference_jarochito/stock_diference_jarochito/objects/<model("stock_diference_jarochito.stock_diference_jarochito"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_diference_jarochito.object', {
#             'object': obj
#         })