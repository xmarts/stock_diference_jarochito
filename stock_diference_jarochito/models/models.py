# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
	"""Agrega campos al stock.move"""
	_inherit = 'stock.move'
	return_qty = fields.Float(
	    string='Cantidad Retornada',
	)
	sale_qty = fields.Float(
	    string='Cantidad Vendida',
	)
	diference_qty = fields.Float(
	    string='Diferencia',
	)
	
class StockPicking(models.Model):
	"""Agrega campos al stock.picking"""
	_inherit = 'stock.picking'
	is_to_route = fields.Boolean(string='Para Ruta')
	user_route_id = fields.Many2one(comodel_name='res.user', string='Usuario de ruta')

class PosSession(models.model):
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