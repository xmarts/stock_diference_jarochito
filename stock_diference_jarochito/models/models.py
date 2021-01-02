
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp

class StockMoveRoute(models.Model):
	"""Agrega tabla para diferencias de entrega al stock.picking"""
	_name = 'stock.move.route'

	product_id = fields.Many2one('product.product', string='Producto Cargado')
	charge_qty = fields.Float(
		string='Cantidad Cargada',
	)

	qty_anterior = fields.Float(string='Cantidad anterior', default=0)

	return_qty = fields.Float(
		string='Cantidad Retornada',
	)
	sale_qty = fields.Float(
		string='Cantidad Vendida',readonly=True
	)
	diference_qty = fields.Float(
		string='Diferencia',
		compute="compute_diference"
	)
	stock_picking_id = fields.Many2one("stock.picking")
	price = fields.Float(string='Precio Empleado')
	price_diference = fields.Float(string='Diferencia $')

	@api.one
	def compute_diference(self):
		self.diference_qty = self.charge_qty - self.return_qty - self.sale_qty

class PosOrder(models.Model):
	_inherit = 'pos.order'

	@api.multi
	def force_cancel(self):
		self.state = 'draft'


class StockPicking(models.Model):
	"""Agrega campos al stock.picking"""
	_inherit = 'stock.picking'
	is_to_route = fields.Boolean(string='Para Ruta')
	user_route_id = fields.Many2one(comodel_name='res.user', string='Usuario de ruta')
	route_moves = fields.One2many('stock.move.route','stock_picking_id', string='Tabla Diferencias')
	ruta = fields.Many2one('res.zona', string="Ruta")
	chofer = fields.Many2one('hr.employee',string="Chofer", related="ruta.user_id")
	interno = fields.Boolean(string="Orden de ruta")
	subpedido_id = fields.Many2one('pos.order',string="pedido venta",readonly=True)
	diference_total = fields.Float(string="Total diferencia", digits=(12,4))
	total_difencia = fields.Integer(string="Total diferencia", digits=(12,4))
	liquida_ruta = fields.Boolean(string="Liquidar Ruta", default=False)
	pos_confi = fields.Many2one('pos.config',string="Punto venta", related="ruta.pos_id")
	pos_secion = fields.Many2one('pos.session',string="Sesion POS", domain="[('config_id','=',pos_confi)]")
	ruta_liquidada = fields.Boolean(string="Liquidada", default=False)
	seccond_transfer = fields.Boolean(string="Es una Recarga", default=False)
	liqui = fields.Boolean(string="Es una Liquidacion", default=False)
	stock_pi = fields.Many2one('stock.picking', string='Carga anterior')
	# CAMPOS DE DELIVERY

	# carrier_price = fields.Float(string="Shipping Cost")
	# delivery_type = fields.Selection(related='carrier_id.delivery_type', readonly=True)
	# carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
	# volume = fields.Float(copy=False)
	# weight = fields.Float(compute='_cal_weight', digits=dp.get_precision('Stock Weight'), store=True, compute_sudo=True)
	# carrier_tracking_ref = fields.Char(string='Tracking Reference', copy=False)
	# carrier_tracking_url = fields.Char(string='Tracking URL', compute='_compute_carrier_tracking_url')
	# weight_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', compute='_compute_weight_uom_id', help="Unit of measurement for Weight")
	# package_ids = fields.Many2many('stock.quant.package', compute='_compute_packages', string='Packages')
	# weight_bulk = fields.Float('Bulk Weight', compute='_compute_bulk_weight')
	# shipping_weight = fields.Float("Weight for Shipping", compute='_compute_shipping_weight')
	def buscar_anterior(self):
		# picking_id = self.env['stock.picking'].search([('id', '=', self.stock_pi)])
		for rec in self.stock_pi.route_moves:
			print('qqqqqqqqqqqqqqq',rec.product_id)
			for moves in self.route_moves:
				#print('aaaaaaaaaaaaaa', moves.product_id)
				if rec.product_id in moves.product_id:
					moves.qty_anterior = rec.charge_qty
					print('ccccccccccccc', moves.product_id)
		# print('aaaaaaaaaaaaaaaaaaaaaaaa')
		# productos = []
		# cantidad = []
		# for picking in self.stock_pi.route_moves:
		# 	productos.append(picking.product_id.id)
		# 	cantidad.append(picking.charge_qty)
		# print('PRODUCTOSSSSSSSSSSS Anteriores', productos)
		# nuevo_pro = []
		# for rec in self.route_moves:
		# 	if rec.product_id.id in (productos):
		# 		print('qqqqqqqqqqqqqqqqqq', )
			#nuevo_pro.append(rec.product_id.id)
			# print('Nueeeeeeeeeevo', nuevo_pro)

			# if picking.pos_secion.id == picking.stock_pi.pos_secion.id:
			# 	for moves in picking.route_moves:
			# 		if picking.route_moves.product_id in (moves.product_id):
			# 			picking.route_moves.qty_anterior = moves.charge_qty
		# 	productos.append(moves.product_id)
		# for rec in self:
		# 	if rec.stock_pi.pos_secion.id == rec.pos_secion.id:
		# 			if rec.product_id in productos:
		# 				print(rec.charge_qty)
		# 				moves.route_moves.qty_anterior = rec.charge_qty
		# else:
		# 	print('ta vacio')

	@api.onchange('pos_confi')
	def onchange_pos_confi(self):

		last_session = self.env['pos.session'].search([('config_id','=',self.pos_confi.id)],limit=1)
		if self.interno == True:
			if last_session.state == 'opened':
				print(last_session)
				self.pos_secion = last_session.id
			else:
				raise ValidationError(_(" Error, necesitas tener una sesión abierta en punto de venta"))

	@api.multi
	def change_route_moves(self):
		self.route_moves = [(5, 0, 0)]
		res = {'value':{'route_moves':[],}}
		# for x in self.move_ids_without_package:
		# 	self.route_moves.create({
		# 		'product_id': x.product_id.id,
		# 		'charge_qty': x.quantity_done,
		# 		'stock_picking_id': self.id,
		# 	})
		# 	print("PRODUCTO >>>>>>>>>>>>>>>>>> ",x.product_id.name)
		self.buscar_anterior()
		prods = self.env['stock.quant'].search([('location_id','=',self.location_dest_id.id)])
		for x in prods:
			e = False
			for z in self.route_moves:
				if z.product_id == x.product_id:
					z.charge_qty += x.quantity
					e = True
			if e == False:
				if x.quantity > 0:
					price_unit = 0
					if self.chofer.address_home_id.property_product_pricelist:
						pricelist = self.chofer.address_home_id.property_product_pricelist
						producttmpl = self.env['product.template'].search([('id','=',x.product_id.product_tmpl_id.id)])
						productpricelist = pricelist.item_ids.search([('product_tmpl_id','=',producttmpl.id),('pricelist_id','=',pricelist.id)], limit=1)
						if productpricelist:
							price_unit = productpricelist.fixed_price
						else:
							price_unit = x.product_id.lst_price
					else:
						price_unit = x.product_id.lst_price
					self.route_moves.create({
						'product_id': x.product_id.id,
						'charge_qty': x.quantity,
						'stock_picking_id': self.id,
						'price':price_unit
						
					})
		if self.seccond_transfer == True:
			searc_pedido = self.env['pos.order'].search([('session_id','=',self.pos_secion.id),])
			for moves in self.route_moves:
				searc_lines = self.env['pos.order.line'].search([('order_id','in',searc_pedido.ids),('product_id','=',moves.product_id.id)])
				for line in searc_lines:
					print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', moves.product_id.name)
					moves.charge_qty += line.qty
				moves.write({'diference_qty': 0.0})
			self.product_pos()

		# self.buscar_anterior()
		self.pos_secion.stock_picking_id = self.id



	@api.multi
	def product_pos(self):
		# self._function_route_moves()
		self.diference_total = 0.0
		if self.pos_confi.validate_session == False:
			mobile_orders = self.env['mobile.order'].search([('pos_session','=', self.pos_secion.id)])
			for rec in mobile_orders:
				if not rec.pos_order_id:
					rec.action_create_pos_order()


			if self.interno == True:
				searc_pedido = self.env['pos.order'].search([('session_id','=',self.pos_secion.id),('state','=','paid')])
				dif = 0.0
				for x in self.route_moves:
					searc_lines = self.env['pos.order.line'].search([('order_id','in',searc_pedido.ids),('product_id','=',x.product_id.id)])
					# if  searc_lines:
					x.sale_qty = 0.0
					if self.seccond_transfer == False and  self.liqui == False:
						x.update({'price_diference': 0.0})
						x.update({'return_qty': x.charge_qty})
						x.return_qty = x.charge_qty
					elif self.seccond_transfer == True and self.liqui == False:
						x.update({'price_diference': 0.0})
						x.update({'return_qty': x.charge_qty})
						x.return_qty = x.charge_qty
					else:
						if self.seccond_transfer == False and self.liqui == True:
							self.diference_total = 0
							for line in searc_lines:
								print('ssssssssssssssss',line.qty)
								x.sale_qty += line.qty
							dif += x.charge_qty - x. return_qty - x.sale_qty
							self.diference_total = dif
							if x.diference_qty > 0.0 and x.price:
								val = x.diference_qty * x.price
								x.write({'price_diference': val})
								print("DIFERENCIA: ",self.diference_total)
			# for x in self.route_moves:
			# if self.diference_total > 0.0:

				self.liquida_ruta = True
			else:
				self.liquida_ruta = False
		else:
			raise UserError("La session de la applicacion aun sigue abierta, favor de cerrar la session para continuar con la operacion")
	# @api.multi
	# def write(self, values):
	# 	record = super(StockPicking, self).write(values)
	# 	if self.interno == True and self.liquida_ruta == True and not self.subpedido_id:
	# 		raise ValidationError('Alerta! \n Es necesario liquidar la ruta.')
	# 	else:
	# 		return record
	@api.multi
	def button_validate(self):
		res = super(StockPicking, self).button_validate()
		if self.interno == True and self.pos_confi != False:
			self.change_route_moves()
		# raise ValidationError("ooooooooooooooooo")
		return res

	@api.onchange('route_moves')
	def _function_route_moves(self):
		dif = 0.0
		# resta = 0.0
		if self.seccond_transfer == False:
			for x in self.route_moves:
				dif += x.charge_qty - x. return_qty - x.sale_qty
			self.diference_total = dif
			print(dif, 'qqqqqqqqqqqqqqqqqqqqqqqqq')
		else:
			dif = 0.0
		# return dif

	@api.multi
	def create_venta_dos(self):
		print('diferencia', self.diference_total)
		# diferencia = self._function_route_moves()
		# print(diferencia)
		if self.diference_total > 0.0:
			print('Enrtraaaaaaaaaa', self.diference_total)
			for r in self.route_moves:				
				total = r.diference_qty * r.product_id.lst_price
				
			if self.chofer.address_home_id:
				defaults = self.env['stock.picking'].default_get(['name', 'picking_type_id'])
				n = self.pos_confi.picking_type_id.sequence_id.next_by_id()
				print("NAME: ",n)
				stock = {
					'name': n,
					'location_id' : self.location_dest_id.id,
					'move_type' : 'direct',
					'state' : 'done',
					'priority' : '1',
					'scheduled_date': datetime.now(),
					'date': datetime.now(),
					# 'user_id' : self.env.user_id.id,
					'date_done': datetime.now(),
					'location_dest_id' : self.pos_confi.picking_type_id.default_location_dest_id.id,
					'picking_type_id' : self.pos_confi.picking_type_id.id, #automatizar
					'is_locked' : 'true',
					'immediate_trasfer' : 'false'
				}

				stockpicking = self.env['stock.picking'].create(stock)

				so=self.env['pos.order'].create({'name': self.env['ir.sequence'].next_by_code('pos.order') or _('New'),
					'session_id':self.pos_secion.id,
					'amount_tax':0,
					'state':'paid',
					'amount_total':total,
					'amount_paid':total,
					'amount_return':0,
					'partner_id': self.chofer.address_home_id.id,
					'picking_id': stockpicking.id

					})
				so.update({'branch_id': self.pos_confi.stock_location_id.branch_id.id})
				self.subpedido_id = so.id
				for lx in self:
					total = 0
					impuestos = 0
					if lx.route_moves:
						con = 0 
						for line in lx.route_moves:
							if line.diference_qty > 0 :
								con += 1
								price_unit = line.price
								total += line.price * line.diference_qty
								price = line.price * line.diference_qty
								currency = None
								lista = []
								ieps_amount = 0
								for x in line.product_id.taxes_id:
									ieps = False
									for z in x.tag_ids:
										if z.name == 'IEPS':
											ieps = True
									if ieps == False:
										lista.append(x.id)
								mytaxes = self.env['account.tax'].search([('id','in',lista)])
								taxes = mytaxes.compute_all(price, currency, 1, product=line.product_id, partner=self.chofer.address_home_id)
								price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else price
								price_total = taxes['total_included'] if taxes else price_subtotal
								
								
								impuestos += price_total - price_subtotal
								self.env['pos.order.line'].create({
									'product_id': line.product_id.id,
									'qty':line.diference_qty,
									'price_unit':price_unit,
									'tax_ids':[(6,0,line.product_id.taxes_id.ids)], 
									'price_subtotal': price_subtotal,
									'price_subtotal_incl':price_total,#taxes['total_included'], 
									'order_id': so.id
									})	
								stockline= {
									'name' : so.name,
									'sequence' : '10',
									'priority' : '1',
									'date': datetime.now(),
									'date_expected': datetime.now(),
									'product_id' : line.product_id.id,
									#'product_qty' : pedido['cantidad'],
									'product_uom_qty' : float(line.diference_qty),
									'reserved_availability' : float(line.diference_qty),
									'quantity_done' : float(line.diference_qty),
									'product_uom' : line.product_id.uom_id.id,
									'location_id': self.location_dest_id.id,
									'location_dest_id': self.pos_confi.picking_type_id.default_location_dest_id.id,
									'picking_type_id' : self.pos_confi.picking_type_id.id, #automatizar
									'picking_id' : stockpicking.id,
									'state' : 'draft',
									'price_unit' : str(price_unit * -1),
									'value': str(price_unit * -1),
									'procure_method' : 'make_to_stock',
									'scrapped' : 'false',
									'propagate' : 'true',
									'aditional' : 'false',
									'to_refud' : 'false',
									'remaining_qty': str(float(line.diference_qty)*-1),
									'remaining_value': str(price_subtotal * -1),
								}
								stockpickingmove = self.env['stock.move'].create(stockline)
					self.subpedido_id.amount_total = total	
					self.subpedido_id.amount_paid = total	
					self.subpedido_id.amount_tax = impuestos	
					statement = self.env['account.bank.statement'].search([('pos_session_id','=',self.pos_secion.id)])
					vars = {
						'name' : so.name,
						'date' : date.today(),
						'amount' : total,
						'account_id' : self.chofer.address_home_id.property_account_receivable_id.id,
						'statement_id' : statement.id,
						'journal_id' : self.pos_confi.journal_id.id,
						'ref' : self.pos_secion.name,
						'sequence' : '1',
						'company_id' : self.pos_confi.company_id.id,
						'pos_statement_id' : self.subpedido_id.id,
						'partner_id' : self.chofer.address_home_id.id,
					}	
					self.env['account.bank.statement.line'].create(vars)
				try:
					stockpicking.action_confirm()
					stockpicking.action_assign()
					x = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, stockpicking.id)]})
					x.process()
				except:
					print("NO PUDO CONCLUIRSE SALIDA DE INVENTARIO")
			else:
				raise ValidationError('Este empleado no tiene direccion privada, asignale una direccion')
			self.ruta_liquidada = True
		self.ruta_liquidada = True




class returns_tras(models.TransientModel):
	_inherit = 'stock.return.picking'

	def returs_pedido(self):
		obj_stock = self.env['stock.picking'].search([('id', '=', self.picking_id.id)], limit=1)
		if obj_stock:
			if obj_stock.interno == True:
				if obj_stock.diference_total > 0.0:
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


	@api.multi
	def action_pos_session_validate(self):
		for rec in self:
			zona = self.env['res.zona'].search([('pos_id', '=', rec.config_id.id)])
			for z in zona:
				print('zzzzzzzzzzzzzzzzzzzzzzzzzzzz', z.codigo)
				res = self.env['res.partner'].search([('zona', '=', z.id)])
				for partner in res:
					print('partner', partner.name)
					emp = self.env['hr.employee'].search([('address_home_id', '=', partner.id)])
					for empleado in emp:
						print('EMPLEADOOOOOOOOOOOOOOOO', empleado.name)
						if empleado.ruta_open == True:
							empleado.ruta_open = False

			pos_order = self.env['pos.order'].search([('session_id', '=', rec.id)])
			for order in pos_order:
				if order.amount_total == 0:
					print('Lineas en 0')
					if order.lines:
						pass
					else:
						order.force_cancel()
						order.unlink()
		return super(PosSession, self).action_pos_session_validate()


class PosConfig(models.Model):
	_inherit = 'pos.config'


	validate_session = fields.Boolean(string="Validar Sesion Activa", default=False)






# class stock_diference_jarochito(models.Model):
#	 _name = 'stock_diference_jarochito.stock_diference_jarochito'

#	 name = fields.Char()
#	 value = fields.Integer()
#	 value2 = fields.Float(compute="_value_pc", store=True)
#	 description = fields.Text()
#
#	 @api.depends('value')
#	 def _value_pc(self):
#		 self.value2 = float(self.value) / 100
#		 