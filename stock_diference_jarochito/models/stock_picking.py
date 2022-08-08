from odoo import fields, models, api
from ast import literal_eval

class StockPicking(models.Model):
    _inherit = "stock.picking"


    orden_ruta = fields.Boolean(
        string="Orden de Ruta"
    )

    zona = fields.Many2one(
        'res.territory',
        string="Ruta"
    )

    person_id = fields.Many2one(
        'fsm.person',
        string="Chofer"
    )

    route_moves = fields.One2many(
        'stock.move.route',
        'picking_id',
        string="Route Moves"
    )

    diference_total = fields.Float(
        string="Total diferencia",
        digits=(12,4)
    )

    # @api.model
    # def create(self, vals):
    #     res = super(StockPicking, self).create(vals)
    #     print(vals)
    #     if vals.get('origin'):
    #         sale_order = self.env['sale.order'].search([
    #             ('name', '=', vals.get('origin'))
    #         ])
    #         print(sale_order.name)
    #         for sale in sale_order:
    #             if sale.sale_traking:
    #                 print(vals['move_line_ids_without_package'], vals['move_ids_without_package'])
    #     return res

    def change_route_moves(self):
        for rec in self:
            if rec.location_dest_id:
                st_quant = self.env['stock.quant']
                st_quant = st_quant.search([
                    ('location_id', '=', rec.location_dest_id.id )
                ])
                self.env['stock.move.route'].search([
                    ('picking_id', '=', rec.id)
                ]).unlink()
                for quant in st_quant:
                    vals = {
                        'picking_id': rec.id,
                        'product_id': quant.product_id.id,
                        'charge_qty': quant.quantity,
                        'return_qty': quant.quantity,
                        'price': rec.get_price_employee(
                            quant.product_id.product_tmpl_id.id
                        )
                    }
                    self.env['stock.move.route'].create(vals)
                # for move_lines in rec.move_ids_without_package:
                #     for m_roue_line in rec.route_moves:

                #         if  move_lines.product_id.id == m_roue_line.product_id.id:
                #             m_roue_line.charge_qty += move_lines.product_uom_qty
                #     product_exist = rec.product_in_route_lines(move_lines.product_id.id, rec.id)
                #     if product_exist:
                #         continue
                #     else:
                #         self.env['stock.move.route'].create({
                #             'picking_id': rec.id,
                #             'product_id': move_lines.product_id.id,
                #             'charge_qty': move_lines.product_uom_qty,
                #         })

    def get_price_employee(self, product_id):
        for rec in self.person_id.partner_id.property_product_pricelist:
            for lines in rec.item_ids:
                if lines.product_tmpl_id.id == product_id:
                    return lines.fixed_price

    def product_in_route_lines(self, product_id, picking_id):
        moves = self.env['stock.move.route'].search([
            ('product_id', '=', product_id),
            ('picking_id', '=', picking_id)
        ])
        if moves:
            return True
        else: return False         
                
    def calculate_diferences(self):

        sale_confirm = self.env['sale.order'].search([
            ('state', '=', 'sale'),
            ('sale_confirm', '=', True),
            ('sale_traking', '=', True),
            ('zona_pre', '=', self.zona.id),
            ('person_id', '=', self.person_id.id)
        ])
        for s_con in sale_confirm:
            s_con = s_con.button_automizate_confirm_orders()
            print(s_con.name, s_con.invoice_status)
            if s_con.invoice_require_app:
                action = self.env["ir.actions.actions"]._for_xml_id("sale.action_view_sale_advance_payment_inv")
                context = literal_eval(action.get('context', "{}"))
                context.update({
                    'active_id': s_con.id if len(self) == 1 else False,
                    'active_ids': s_con.id,
                    'default_company_id': s_con.company_id.id,
                    'default_advance_payment_method': 'delivered'
                })
                action['context'] = context
                invoice_create = self.env['sale.advance.payment.inv'].with_context(action).create({})
                print(invoice_create)
                invoice_create._create_invoice(s_con, s_con.order_line, s_con.amount_total)
        for move_lines in self.route_moves:
            total = self.get_qty_sale(move_lines.product_id.id)
            move_lines.sale_qty = total
        self.diference_total = 0
        for rec in self.route_moves:
            self.diference_total += rec.diference_qty

    def get_qty_sale(self, product_id):
        sale_order = self.env['sale.order'].search([
            ('state', '=', 'sale'),
            ('sale_confirm', '=', True),
            ('sale_traking', '=', True),
            ('zona_pre', '=', self.zona.id),
            ('person_id', '=', self.person_id.id)
        ]).ids
        total = sum(self.env['sale.order.line'].search([
            ('order_id', 'in', sale_order),
            ('product_id', '=', product_id)
        ]).mapped('product_uom_qty'))
        return total


class StockMoveRoute(models.Model):
    _name = "stock.move.route"

    
    picking_id = fields.Many2one(
        'stock.picking',
        string="Picking"
    )

    product_id = fields.Many2one(
        'product.product',
        string="Producto"
    )

    charge_qty = fields.Float(
        string="Cantidad cargada"
    )

    return_qty = fields.Float(
        string="Cantidad retornada"
    )

    sale_qty = fields.Float(
        string="Cantitdad vendida"
    )

    diference_qty = fields.Float(
        string="Diferencia",
        compute="compute_diference"
    )

    price = fields.Float(
        string="Precio empleado"
    )
    
    @api.depends('charge_qty', 'return_qty', 'sale_qty')
    def compute_diference(self):
        for rec in self:
            rec.diference_qty = rec.charge_qty - rec.return_qty - rec.sale_qty
