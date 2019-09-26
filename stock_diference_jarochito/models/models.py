# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveRoute(models.Model):
	"""Agrega tabla para diferencias de entrega al stock.picking"""
	_name = 'stock.move.route'

	product_id = fields.Many2one('product.product', string='Producto Cargado')
	
	return_qty = fields.Float(
	    string='Cantidad Retornada',
	)
	sale_qty = fields.Float(
	    string='Cantidad Vendida',
	)
	diference_qty = fields.Float(
	    string='Diferencia',
	)
	stock_picking_id = fields.Many2one("stock.picking")
	

class StockPicking(models.Model):
	"""Agrega campos al stock.picking"""
	_inherit = 'stock.picking'
	is_to_route = fields.Boolean(string='Para Ruta')
	user_route_id = fields.Many2one(comodel_name='res.user', string='Usuario de ruta')
	route_moves = fields.One2many('stock.move.route','stock_picking_id', string='Tabla Diferencias')

	@api.depends('move_ids_without_package')
	@api.onchange('move_ids_without_package')
	def _onchange_moves_picking(self):
		for x in self.move_ids_without_package:
			line_ids = []
            res = {'value':{
                    'route_moves':[],
                }
            }
			print("PRODUCTO >>>>>>>>>>>>>>>>>> ",x.product_id.name)


class PosSession(models.Model):
	_inherit = 'pos.session'
	stock_picking_id = fields.Many2one(comodel_name="stock.picking", string="Inventario entregado")

# class stock_diference_jarochito(models.Model):
#     _name = 'stock_diference_jarochito.stock_diference_jarochito'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100