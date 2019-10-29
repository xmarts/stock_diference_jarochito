# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class StockMoveRoute(models.Model):
	"""Agrega tabla para diferencias de entrega al stock.picking"""
	_name = 'stock.move.route'

	product_id = fields.Many2one('product.product', string='Producto Cargado')
	charge_qty = fields.Float(
	    string='Cantidad Cargada',
	)
	return_qty = fields.Float(
	    string='Cantidad Retornada',
	)
	sale_qty = fields.Float(
	    string='Cantidad Vendida',readonly=True
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
	chofer = fields.Many2one('hr.employee',string="Chofer")
	interno = fields.Boolean(string="Orden de ruta")
	subpedido_id = fields.Many2one('pos.order',string="pedido venta",readonly=True)
	total_difencia = fields.Integer(string="Total diferencia")

	pos_confi = fields.Many2one('pos.config',string="Punto venta")
	pos_secion = fields.Many2one('pos.session',string="Seccion", domain="[('config_id','=',pos_confi)]")



	def change_route_moves(self):
		self.route_moves = [(5, 0, 0)]
		res = {'value':{'route_moves':[],}}
		for x in self.move_ids_without_package:
			self.route_moves.create({
				'product_id': x.product_id.id,
				'charge_qty': x.quantity_done,
				'stock_picking_id': self.id,
			})
			print("PRODUCTO >>>>>>>>>>>>>>>>>> ",x.product_id.name)
	
	@api.multi
	def button_validate(self):
		record = super(StockPicking, self).button_validate()
		#if self.state == 'done':
		self.change_route_moves()
		return record

	@api.onchange('route_moves')
	def _function_route_moves(self):
		dif = 0
		resta = 0
		for x in self.route_moves:
			if x.charge_qty and x.return_qty:
				resta = x.charge_qty - x. return_qty
				if x.sale_qty:
					x.diference_qty = resta - x.sale_qty
				else:
					x.diference_qty = 0
			if x.diference_qty:
				dif += x.diference_qty
		self.total_difencia = dif
	

	@api.multi
	def create_venta_dos(self):
		if self.total_difencia >0:
			for r in self.route_moves:				
				total = r.diference_qty * r.product_id.lst_price
				
			if self.chofer.user_id:
				so=self.env['pos.order'].create({'name': self.env['ir.sequence'].next_by_code('pos.order') or _('New'),
					'session_id':self.pos_secion.id,
					'amount_tax':0,
					'amount_total':total,
					'amount_paid':total,
					'amount_return':0,

					})
				self.subpedido_id = so.id
				for lx in self:
					if lx.route_moves:
						con = 0 
						for line in lx.route_moves:
							if line.diference_qty >0 :
								con += 1
								neto = line.diference_qty * line.product_id.lst_price
								self.env['pos.order.line'].create({
		                            'product_id': line.product_id.id,
		                            'qty':line.diference_qty,
		                            'price_unit':line.product_id.lst_price,
		                            'tax_ids_after_fiscal_position':'IVA(0%) VENTAS', 
		                            'price_subtotal': neto,
		                            'price_subtotal_incl':neto, 
		                            'order_id': so.id
		                            })							
			else:
				raise ValidationError('Este empleado no tiene usuario, asignale un usuario')
	@api.multi
	def product_pos(self):
		if self.interno == True:
			searc_pedido = self.env['pos.order'].search([('session_id','=',self.pos_secion.id),])
			for x in self.route_moves:
				searc_lines = self.env['pos.order.line'].search([('order_id','in',searc_pedido.ids),('product_id','=',x.product_id.id)])
				if  searc_lines:
					x.sale_qty = 0	
					for line in searc_lines:
						x.sale_qty += line.qty
				else:
					x.sale_qty = 0		
					




class returns_tras(models.TransientModel):
	_inherit = 'stock.return.picking'

	def returs_pedido(self):
		obj_stock = self.env['stock.picking'].search([('id', '=', self.picking_id.id)], limit=1)
		if obj_stock:
			if obj_stock.interno == True:
				if obj_stock.total_difencia >0:
					sale = self.env['sale.order'].search([('name','=',obj_stock.subpedido_id.name)])
					if sale:
						if sale.state == 'sale':
							return super(returns_tras,self).create_returns()
						else:
							raise ValidationError('Pedido no validado')
				else:
					return super(returns_tras,self).create_returns()								
			else:
				return super(returns_tras,self).create_returns()							



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
#         